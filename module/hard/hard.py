import importlib

from module.base.ocr import Digit
from campaign.campaign_hard.campaign_hard import Campaign
from module.campaign.run import CampaignRun
from module.hard.assets import *
from module.logger import logger

OCR_HARD_REMAIN = Digit(OCR_HARD_REMAIN, letter=(123, 227, 66), back=(24, 24, 24), limit=3, name='OCR_HARD_REMAIN')
RECORD_OPTION = ('DailyRecord', 'hard')
RECORD_SINCE = (0,)


class CampaignHard(CampaignRun):
    equipment_has_take_on = False
    campaign: Campaign

    def run(self):
        logger.hr('Campaign hard', level=1)
        chapter, stage = self.config.HARD_CAMPAIGN.split('-')
        name = f'campaign_{chapter}_{stage}'

        # Initial
        self.load_campaign(name='campaign_hard', folder='campaign_hard')  # Load campaign file
        module = importlib.import_module('.' + name, 'campaign.campaign_main')  # Load map from normal mode.
        self.campaign.MAP = module.MAP
        self.campaign_name_set(name + '_HARD')
        if self.equipment_has_take_on:
            self.campaign.equipment_has_take_on = True

        # UI ensure
        self.ui_weigh_anchor()
        self.campaign_ensure_mode(mode='normal')
        self.campaign_ensure_chapter(index=int(chapter))
        self.campaign_ensure_mode(mode='hard')
        self.campaign.ENTRANCE = self.campaign_get_entrance(name=f'{chapter}-{stage}')

        # Run
        remain = OCR_HARD_REMAIN.ocr(self.device.image)
        logger.attr('Remain', remain)
        for n in range(remain):
            self.campaign.run()

        self.campaign.equipment_take_off_when_finished()

    def record_executed_since(self):
        return self.config.record_executed_since(option=RECORD_OPTION, since=RECORD_SINCE)

    def record_save(self):
        return self.config.record_save(option=RECORD_OPTION)
