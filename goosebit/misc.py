from __future__ import annotations

from typing import Optional

import semver

from goosebit.models import Device, FirmwareCompatibility, FirmwareUpdate


async def get_newest_fw(hw_model: str, hw_revision: str) -> Optional[str]:
    compatibility = await FirmwareCompatibility.get_or_none(
        hw_model=hw_model, hw_revision=hw_revision
    )
    firmware = await FirmwareUpdate.filter(compatibility=compatibility).all()
    if len(firmware) == 0:
        return None

    return str(
        sorted(firmware, key=lambda x: semver.Version.parse(x.version), reverse=True)[
            0
        ].path
    )


def validate_filename(filename: str) -> bool:
    return filename.endswith(".swu")


async def get_device_by_uuid(dev_id: str) -> Device:
    if dev_id == "unknown":
        return Device(
            uuid="unknown",
            name="Unknown",
            fw_file="latest",
            fw_version=None,
            last_state=None,
            last_log=None,
        )
    return (await Device.get_or_create(uuid=dev_id))[0]
