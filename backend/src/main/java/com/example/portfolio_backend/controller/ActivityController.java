package com.example.portfolio_backend.controller;

import com.example.portfolio_backend.dto.ActivityResponseDTO;
import com.example.portfolio_backend.service.ActivityService;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/activity")
public class ActivityController {

  private final ActivityService service;

  public ActivityController(ActivityService service) {
    this.service = service;
  }

  @GetMapping
  public ActivityResponseDTO getActivity(@RequestParam(defaultValue = "1y") String range) {
    return service.getActivity(range);
  }
}