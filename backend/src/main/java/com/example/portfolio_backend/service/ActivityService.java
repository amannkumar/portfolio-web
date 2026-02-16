package com.example.portfolio_backend.service;

import com.example.portfolio_backend.dto.ActivityDayDTO;
import com.example.portfolio_backend.dto.ActivityResponseDTO;
import com.example.portfolio_backend.model.DailyActivity;
import com.example.portfolio_backend.repository.DailyActivityRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class ActivityService {

  private final DailyActivityRepository repo;

  public ActivityService(DailyActivityRepository repo) {
    this.repo = repo;
  }

  public ActivityResponseDTO getActivity(String range) {
    LocalDate end = LocalDate.now();
    LocalDate start = switch (range) {
      case "30d" -> end.minusDays(29);
      case "90d" -> end.minusDays(89);
      case "1y" -> end.minusDays(364);
      default -> end.minusDays(364);
    };

    // Load from DB
    List<DailyActivity> rows = repo.findByDateBetweenOrderByDateAsc(start, end);

    // Convert rows -> map
    Map<LocalDate, DailyActivity> byDate =
        rows.stream().collect(Collectors.toMap(DailyActivity::getDate, r -> r, (a, b) -> a));

    // Return continuous days (fill missing as zeros)
    List<ActivityDayDTO> days = new ArrayList<>();
    for (LocalDate d = start; !d.isAfter(end); d = d.plusDays(1)) {
      DailyActivity r = byDate.get(d);
      if (r == null) {
        days.add(new ActivityDayDTO(d.toString(), 0, 0, 0));
      } else {
        days.add(new ActivityDayDTO(
            r.getDate().toString(),
            r.getTotalCount(),
            r.getLeetcodeCount(),
            r.getGithubCount()
        ));
      }
    }

    return new ActivityResponseDTO(range, days);
  }
}
