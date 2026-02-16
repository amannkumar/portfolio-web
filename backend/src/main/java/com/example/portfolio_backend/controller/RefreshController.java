package com.example.portfolio_backend.controller;

import com.example.portfolio_backend.service.ActivityIngestService;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;

@RestController
@RequestMapping("/api/activity")
public class RefreshController {

  private final ActivityIngestService ingest;

  public RefreshController(ActivityIngestService ingest) {
    this.ingest = ingest;
  }

  @PostMapping("/refresh")
  public String refresh(@RequestParam(defaultValue = "1y") String range) {
    LocalDate end = LocalDate.now();
    LocalDate start = switch (range) {
      case "30d" -> end.minusDays(29);
      case "90d" -> end.minusDays(89);
      default -> end.minusDays(364);
    };

    ingest.refreshRange(start, end);
    return "ok";
  }
}
