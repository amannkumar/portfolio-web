package com.example.portfolio_backend.dto;

public record ActivityDayDTO(
    String date,   // "YYYY-MM-DD"
    int total,
    int leetcode,
    int github
) {}