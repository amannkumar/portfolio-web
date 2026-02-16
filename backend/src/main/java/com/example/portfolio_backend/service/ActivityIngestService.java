package com.example.portfolio_backend.service;

import com.example.portfolio_backend.model.DailyActivity;
import com.example.portfolio_backend.repository.DailyActivityRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.Map;

@Service
public class ActivityIngestService {

  private final DailyActivityRepository repo;
  private final GitHubService gitHubService;
  private final LeetCodeService leetCodeService;

  public ActivityIngestService(
      DailyActivityRepository repo,
      GitHubService gitHubService,
      LeetCodeService leetCodeService
  ) {
    this.repo = repo;
    this.gitHubService = gitHubService;
    this.leetCodeService = leetCodeService;
  }

  public void refreshRange(LocalDate start, LocalDate end) {
    Map<LocalDate, Integer> github = gitHubService.getContributionCalendar(start, end);
    Map<LocalDate, Integer> leetcode = leetCodeService.getSubmissionCalendar(start, end);

    for (LocalDate d = start; !d.isAfter(end); d = d.plusDays(1)) {
      int gh = github.getOrDefault(d, 0);
      int lc = leetcode.getOrDefault(d, 0);

      DailyActivity row = repo.findByDate(d).orElseGet(DailyActivity::new);
      row.setDate(d);
      row.setGithubCount(gh);
      row.setLeetcodeCount(lc);

      repo.save(row);
    }
  }
}
