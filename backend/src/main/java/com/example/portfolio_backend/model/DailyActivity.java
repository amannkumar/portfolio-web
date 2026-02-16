package com.example.portfolio_backend.model;

import jakarta.persistence.*;
import java.time.LocalDate;
import java.time.OffsetDateTime;

@Entity
@Table(
    name = "daily_activity",
    uniqueConstraints = @UniqueConstraint(columnNames = {"activity_date"})
)
public class DailyActivity {

  @Id
  @GeneratedValue(strategy = GenerationType.UUID)
  private java.util.UUID id;

  @Column(name = "activity_date", nullable = false)
  private LocalDate date;

  @Column(name = "leetcode_count", nullable = false)
  private int leetcodeCount = 0;

  @Column(name = "github_count", nullable = false)
  private int githubCount = 0;

  @Column(name = "total_count", nullable = false)
  private int totalCount = 0;

  @Column(name = "updated_at", nullable = false)
  private OffsetDateTime updatedAt = OffsetDateTime.now();

  public DailyActivity() {}

  public DailyActivity(LocalDate date, int leetcodeCount, int githubCount) {
    this.date = date;
    this.leetcodeCount = leetcodeCount;
    this.githubCount = githubCount;
    this.totalCount = leetcodeCount + githubCount;
    this.updatedAt = OffsetDateTime.now();
  }

  @PrePersist
  @PreUpdate
  void preUpdate() {
    this.totalCount = this.leetcodeCount + this.githubCount;
    this.updatedAt = OffsetDateTime.now();
  }

  // Getters & Setters

  public java.util.UUID getId() { return id; }

  public LocalDate getDate() { return date; }
  public void setDate(LocalDate date) { this.date = date; }

  public int getLeetcodeCount() { return leetcodeCount; }
  public void setLeetcodeCount(int leetcodeCount) { this.leetcodeCount = leetcodeCount; }

  public int getGithubCount() { return githubCount; }
  public void setGithubCount(int githubCount) { this.githubCount = githubCount; }

  public int getTotalCount() { return totalCount; }

  public OffsetDateTime getUpdatedAt() { return updatedAt; }
}
