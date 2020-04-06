from datetime import datetime, timedelta

from module.base.timer import Timer
from module.combat.assets import *
from module.logger import logger
from module.reward.assets import *
from module.ui.page import *
from module.reward.commission import RewardCommission


class Reward(RewardCommission):
    def reward(self):
        logger.hr('Reward start')
        self.ui_goto_main()
        self._reward_mission()

        self.ui_goto(page_reward, skip_first_screenshot=True)

        self._reward_receive()
        self.handle_info_bar()
        self.handle_commission_start()

        self.ui_click(
            click_button=page_reward.links[page_main],
            check_button=page_main.check_button,
            appear_button=page_reward.check_button,
            skip_first_screenshot=True)
        logger.hr('Reward end')

    def handle_reward(self):
        if not self.config.ENABLE_REWARD:
            return False
        if datetime.now() - self.config.REWARD_LAST_TIME < timedelta(minutes=self.config.REWARD_INTERVAL):
            return False

        self.reward()

        self.config.REWARD_LAST_TIME = datetime.now()
        return True

    def _reward_receive(self):
        """
        Returns:
            bool: If rewarded.
        """
        logger.hr('Oil Reward')

        reward = False
        exit_timer = Timer(1)
        click_timer = Timer(1)
        exit_timer.start()
        btn = []
        if self.config.ENABLE_REWARD:
            btn.append(REWARD_3)
        if self.config.ENABLE_COMMISSION_REWARD:
            btn.append(REWARD_1)
        if self.config.ENABLE_OIL_REWARD:
            btn.append(OIL)
        if self.config.ENABLE_COIN_REWARD:
            btn.append(COIN)

        while 1:
            self.device.screenshot()

            for button in [EXP_INFO_S_REWARD, GET_ITEMS_1, GET_ITEMS_2, GET_SHIP]:
                if self.appear(button, interval=1):
                    self.device.click(REWARD_SAVE_CLICK)
                    exit_timer.reset()
                    reward = True
                    continue

            for button in btn:
                if not click_timer.reached():
                    continue
                if self.appear_then_click(button, interval=1):
                    exit_timer.reset()
                    click_timer.reset()
                    reward = True
                    continue

            # End
            if exit_timer.reached():
                break

        return reward

    def _reward_mission(self):
        """
        Returns:
            bool: If rewarded.
        """
        logger.hr('Mission reward')
        if not self.appear(MISSION_NOTICE):
            logger.info('No mission reward')
            return False

        self.ui_goto(page_mission, skip_first_screenshot=True)

        reward = False
        exit_timer = Timer(1)
        click_timer = Timer(1)
        exit_timer.start()
        while 1:
            self.device.screenshot()

            for button in [GET_ITEMS_1, GET_ITEMS_2, GET_SHIP]:
                if self.appear_then_click(button, interval=1):
                    exit_timer.reset()
                    reward = True
                    continue

            for button in [MISSION_MULTI, MISSION_SIGNAL]:
                if not click_timer.reached():
                    continue
                if self.appear_then_click(button, interval=1):
                    exit_timer.reset()
                    click_timer.reset()
                    reward = True
                    continue

            # End
            if exit_timer.reached():
                break

        self.ui_goto(page_main, skip_first_screenshot=True)
        return reward
