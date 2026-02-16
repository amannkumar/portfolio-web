package com.example.portfolio_backend.dto;

import java.util.List;

public record ActivityResponseDTO(
    String range,
    List<ActivityDayDTO> days
) {}
