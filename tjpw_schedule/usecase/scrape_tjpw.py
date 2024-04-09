from tjpw_schedule.domain.schedule_external_api import (
    ScheduleExternalApi,
)
from tjpw_schedule.domain.scraper import DetailUrl, Scraper
from tjpw_schedule.usecase.request.scrape_range import ScrapeRange


class ScrapeTjpw:
    def __init__(
        self,
        scraper: Scraper,
        schedule_external_api_list: list[ScheduleExternalApi],
    ) -> None:
        self.scraper = scraper
        self.schedule_external_api_list = schedule_external_api_list

    def execute(self, range: ScrapeRange) -> None:
        for target_yyyymm in range.to_target_yyyymm_list():
            print(f"target_yyyymm: {target_yyyymm}")

            # その月にふくまれる、試合詳細のURL一覧を取得
            detail_urls = self.scraper.get_detail_urls(
                target_year=int(target_yyyymm[:4]),
                target_month=int(target_yyyymm[4:]),
            )
            # 検索範囲内かつ必要なページに絞る
            detail_urls = [
                detail_url
                for detail_url in detail_urls
                if detail_url.is_in_date_range(range.start_date, range.end_date) and detail_url.is_schedule()
            ]

            _ = [self._execute_detail(detail_url) for detail_url in detail_urls]

    def _execute_detail(self, detail_url: DetailUrl) -> None:
        """詳細をスクレイピングして登録する"""
        # スクレイピング
        item_entity = self.scraper.scrape_detail(detail_url.value)
        tournament_schedule = item_entity.convert_to_tournament_schedule()

        # 注入したAPIの分、登録処理を行う
        for schedule_external_api in self.schedule_external_api_list:
            schedule_external_api.save(tournament_schedule)
