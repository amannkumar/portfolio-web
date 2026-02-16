package com.example.portfolio_backend.repository;

import com.example.portfolio_backend.model.DailyActivity;
import org.springframework.data.jpa.repository.JpaRepository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;


public interface DailyActivityRepository extends JpaRepository<DailyActivity, java.util.UUID> {
  List<DailyActivity> findByDateBetweenOrderByDateAsc(LocalDate start, LocalDate end);
  Optional<DailyActivity> findByDate(LocalDate date);
}
