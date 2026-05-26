"""检测 API — 图片上传检测、手动保存图片"""
import io
import os
import time
import base64
import logging
import asyncio
from datetime import datetime

import cv2
import numpy as np
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Request, Query

from objcounter.config import get_config
from objcounter.detector import draw_results
from objcounter.i18n import t
from objcounter.stats import detection_stats
from objcounter.state import app_state
from objcounter.middleware import verify_api_key

logger = logging.getLogger("count_web")
router = APIRouter(tags=["detect"])

detect_semaphore = asyncio.Semaphore(2)


@router.post("/api/detect")
async def detect_image(
    file: UploadFile = File(...),
    conf: float = Query(default=None, ge=0.01, le=1.0),
    iou: float = Query(default=None, ge=0.01, le=1.0),
    _: str = Depends(verify_api_key),
    request: Request = None,
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail={"error": True, "message": t("upload_no_image"), "code": 400})

    content = await file.read()
    max_bytes = get_config("max_upload_mb", 10) * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(status_code=400, detail={"error": True, "message": t("upload_too_large", max=get_config('max_upload_mb')), "code": 400})

    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail={"error": True, "message": t("upload_parse_failed"), "code": 400})

    detector = app_state.detector  # 线程安全读取
    try:
        async with detect_semaphore:
            t0 = time.perf_counter()
            results = await asyncio.to_thread(detector.detect, img, conf=conf, iou=iou)
            elapsed = time.perf_counter() - t0
    except Exception:
        detection_stats.record_error()
        raise HTTPException(status_code=503, detail={"error": True, "message": t("server_busy"), "code": 503})

    if request:
        detection_stats.record_success(client_ip=request.client.host)

    # 优质训练照片筛选 — 异常隔离，不影响检测结果
    saved_valuable = False
    try:
        saved_valuable = app_state.valuable_saver.check_and_save(img, results, filename=file.filename or "image.jpg")
    except Exception as e:
        logger.error(f"优质照片保存失败: {e}")

    vis = draw_results(img, results)
    _, buffer = cv2.imencode(".jpg", vis, [cv2.IMWRITE_JPEG_QUALITY, 90])
    vis_b64 = base64.b64encode(buffer).decode("utf-8")

    return {
        "count": len(results),
        "elapsed_ms": round(elapsed * 1000, 1),
        "detections": results,
        "result_image": f"data:image/jpeg;base64,{vis_b64}",
        "image_size": {"width": img.shape[1], "height": img.shape[0]},
        "valuable_saved": saved_valuable,
        "valuable_count": app_state.valuable_saver.saved_count,
    }


@router.post("/api/save-image")
async def save_image(
    file: UploadFile = File(...),
    _: str = Depends(verify_api_key),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail={"error": True, "message": t("upload_no_image"), "code": 400})
    content = await file.read()
    nparr = np.frombuffer(content, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise HTTPException(status_code=400, detail={"error": True, "message": t("save_parse_failed"), "code": 400})
    vdir = get_config("valuable_dir", "Valuable photos")
    os.makedirs(vdir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = os.path.splitext(file.filename or "image.jpg")[1] or ".jpg"
    save_name = f"manual_{timestamp}{ext}"
    save_path = os.path.join(vdir, save_name)
    cv2.imwrite(save_path, img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    app_state.valuable_saver.increment_count()
    logger.info(f"[MANUAL_SAVE] {save_name}")
    return {"ok": True, "path": save_name}
