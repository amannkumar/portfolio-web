package com.example.portfolio_backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.LocalDate;
import java.util.*;

@Service
public class LeetCodeService {

  private final RestClient client;
  private final String username;

  public LeetCodeService(@Value("${app.leetcode.username}") String username) {
    this.username = username;
    this.client = RestClient.builder()
        .baseUrl("https://leetcode.com")
        .defaultHeader("Content-Type", "application/json")
        .build();
  }

  /**
   * Returns map: date -> submissionCount
   * Best-effort: LeetCode GraphQL. If blocked, returns empty map.
   */
  public Map<LocalDate, Integer> getSubmissionCalendar(LocalDate from, LocalDate to) {
    Map<LocalDate, Integer> out = new HashMap<>();

    String query = """
      query userProfileCalendar($username: String!) {
        matchedUser(username: $username) {
          userCalendar {
            submissionCalendar
          }
        }
      }
      """;

    Map<String, Object> variables = new HashMap<>();
    variables.put("username", username);

    Map<String, Object> payload = new HashMap<>();
    payload.put("query", query);
    payload.put("variables", variables);

    try {
      Map<?, ?> resp = client.post()
          .uri("/graphql")
          .body(payload)
          .retrieve()
          .body(Map.class);

      // Navigate: data.matchedUser.userCalendar.submissionCalendar
      Map<?, ?> data = (Map<?, ?>) resp.get("data");
      if (data == null) return out;

      Map<?, ?> matched = (Map<?, ?>) data.get("matchedUser");
      if (matched == null) return out;

      Map<?, ?> cal = (Map<?, ?>) matched.get("userCalendar");
      if (cal == null) return out;

      String calendarJson = String.valueOf(cal.get("submissionCalendar"));
      // submissionCalendar is a JSON string like {"1695945600": 2, ...} (epoch seconds)
      // parse it:
      @SuppressWarnings("unchecked")
      Map<String, Object> epochMap = new com.fasterxml.jackson.databind.ObjectMapper()
          .readValue(calendarJson, Map.class);

      for (var e : epochMap.entrySet()) {
        long epochSeconds = Long.parseLong(e.getKey());
        int count = ((Number) e.getValue()).intValue();

        LocalDate date = java.time.Instant.ofEpochSecond(epochSeconds)
            .atZone(java.time.ZoneOffset.UTC)
            .toLocalDate();

        if (!date.isBefore(from) && !date.isAfter(to)) {
          out.put(date, count);
        }
      }

      return out;
    } catch (Exception ignored) {
      return out;
    }
  }
}