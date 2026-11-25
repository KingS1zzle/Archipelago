import logging
from typing import TYPE_CHECKING
from NetUtils import ClientStatus
import worlds._bizhawk as bizhawk
from worlds._bizhawk.client import BizHawkClient

if TYPE_CHECKING:
    from worlds._bizhawk.context import BizHawkClientContext

logger = logging.getLogger("Client")
    
class PocketMuuMuuClient(BizHawkClient):
    game = "Pocket MuuMuu"
    system = "PSX"
# patch_suffix = ".apPMM" (use if game needs a patch)
    def __init__(self):
        super().__init__()
        self.items_applied = 0

    async def validate_rom(self, ctx: "BizHawkClientContext") -> bool:
        try:
            # Check for Pocket MuuMuu
            check_byte = ((await bizhawk.read(ctx.bizhawk_ctx, [(0x03D2F4, 1, "MainRAM")]))[0])[0] # Check if Pocket MuuMuu is fully loaded. Player is at the title Screen.
            if check_byte != 0x4D: # Always 0x4D. Use for startup protection (things flicker while starting up).
                return False  # Not Pocket MuuMuu
        except bizhawk.RequestFailedError:
            return False  # Not able to get a response, say no for now

        # This is Pocket MuuMuu
        ctx.game = self.game
        ctx.items_handling = 0b111
        ctx.want_slot_data = True

        return True

    async def game_watcher(self, ctx: "BizHawkClientContext") -> None: # Game_Watcher runs multiple times per second, like a Main would.
        try:
            # Read save data
            save_data = (await bizhawk.read(ctx.bizhawk_ctx,[(0x010994, 1, "MainRAM")]))[0] # DropZone Star 1 - Check

            # Check locations
            if save_data[0] & 0x01 and 7700101 not in ctx.checked_locations:
                await ctx.send_msgs([{
                    "cmd": "LocationChecks",
                    "locations": [7700101]
                }])

            # Give received items, one per loop
            if self.items_applied < len(ctx.items_received): # Checks if there are any items that need to be applyed
                item = ctx.items_received[self.items_applied]

                if item.item == 7700001:  # Money (500)
                    mu_bytes = (await bizhawk.read(ctx.bizhawk_ctx, [(0x010814, 4, "MainRAM")]))[0]
                    mu = int.from_bytes(mu_bytes, "little")
                    mu = mu + 1
                    await bizhawk.write(ctx.bizhawk_ctx, [(0x010814, mu.to_bytes(4, "little"), "MainRAM")])
                    logger.info(f"Gave 1 Mu: {mu - 1} -> {mu}")

                self.items_applied += 1

        except bizhawk.RequestFailedError:
            # The connector didn't respond. Exit handler and return to main loop to reconnect
            pass