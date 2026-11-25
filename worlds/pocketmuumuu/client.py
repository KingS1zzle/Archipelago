from typing import TYPE_CHECKING
from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

    
class PocketMuuMuuClient(BizHawkClient):
    game = "Pocket MuuMuu"
    system = "PSX"
# patch_suffix = ".apPMM"

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # Check for Pocket MuuMuu
            check_byte = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x03D2F4, 1, "MainRAM")]))[0])[0]
            if check_byte != 0x4D:
                return False  # Not Pocket MuuMuu
        except bizhawk.RequestFailedError:
            return False  # Not able to get a response, say no for now

        # This is Pocket MuuMuu
        ctx.game = self.game
        ctx.items_handling = 0b001
        ctx.want_slot_data = True

        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None:
        try:
            # Read save data
            save_data = (await bizhawk.read(ctx.bizhawk_ctx,[(0x01091C, 1, "MainRAM")]))[0]

            # Check locations
            if save_data[0] & 0x01 and 7700101 not in ctx.checked_locations:
                await ctx.send_msgs([{
                    "cmd": "LocationChecks",
                    "locations": [7700101]
                }])

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass