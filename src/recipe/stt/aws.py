"""AWS Transcribe Speech-to-Text."""
from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path

from recipe.stt import SttEngine, register

log = logging.getLogger(__name__)


@register("aws")
class AwsSttEngine(SttEngine):
    """AWS Transcribe (requires boto3)"""

    def __init__(self, **kwargs):
        try:
            import boto3  # noqa: F401
        except ImportError:
            raise RuntimeError("Install the 'aws' extra: uv pip install 'recipe[aws]'")

    def transcribe(self, audio_path: Path, language: str = "zh") -> str:
        import boto3
        import httpx

        s3 = boto3.client("s3")
        transcribe = boto3.client("transcribe")

        bucket = f"recipe-transcribe-{uuid.uuid4().hex[:8]}"
        s3_key = f"audio/{audio_path.name}"
        job_name = f"recipe-{uuid.uuid4().hex[:8]}"

        lang_map = {"zh": "zh-CN", "en": "en-US", "ja": "ja-JP"}
        lang_code = lang_map.get(language, language)

        log.debug("Creating S3 bucket: %s", bucket)
        s3.create_bucket(Bucket=bucket)
        try:
            log.debug("Uploading audio to s3://%s/%s", bucket, s3_key)
            s3.upload_file(str(audio_path), bucket, s3_key)

            transcribe.start_transcription_job(
                TranscriptionJobName=job_name,
                Media={"MediaFileUri": f"s3://{bucket}/{s3_key}"},
                MediaFormat="wav",
                LanguageCode=lang_code,
            )

            while True:
                status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
                state = status["TranscriptionJob"]["TranscriptionJobStatus"]
                if state == "COMPLETED":
                    break
                if state == "FAILED":
                    raise RuntimeError(f"AWS Transcribe job failed: {status}")
                log.debug("Job status: %s, waiting...", state)
                time.sleep(5)

            transcript_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
            resp = httpx.get(transcript_uri)
            resp.raise_for_status()
            data = resp.json()
            text = data["results"]["transcripts"][0]["transcript"]
            log.debug("AWS transcription length: %d chars", len(text))
            return text
        finally:
            # Cleanup
            try:
                s3.delete_object(Bucket=bucket, Key=s3_key)
                s3.delete_bucket(Bucket=bucket)
            except Exception as e:
                log.warning("Failed to cleanup S3 bucket %s: %s", bucket, e)
