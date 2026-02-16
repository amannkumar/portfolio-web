package com.example.portfolio_backend.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.time.LocalDate;
import java.util.*;

@Service
public class GitHubService {

  private final RestClient client;
  private final String username;

  public GitHubService(
      @Value("${app.github.username}") String username,
      @Value("${app.github.token}") String token
  ) {
    this.username = username;
    this.client = RestClient.builder()
        .baseUrl("https://api.github.com")
        .defaultHeader(HttpHeaders.AUTHORIZATION, "Bearer " + token)
        .defaultHeader(HttpHeaders.CONTENT_TYPE, "application/json")
        .build();
  }

  public Map<LocalDate, Integer> getContributionCalendar(LocalDate from, LocalDate to) {
    // GitHub GraphQL expects ISO datetime strings
    String query = """
      query($login: String!, $from: DateTime!, $to: DateTime!) {
        user(login: $login) {
          contributionsCollection(from: $from, to: $to) {
            contributionCalendar {
              weeks {
                contributionDays {
                  date
                  contributionCount
                }
              }
            }
          }
        }
      }
      """;

    Map<String, Object> variables = new HashMap<>();
    variables.put("login", username);
    variables.put("from", from.toString() + "T00:00:00Z");
    variables.put("to", to.toString() + "T23:59:59Z");

    Map<String, Object> payload = new HashMap<>();
    payload.put("query", query);
    payload.put("variables", variables);

    Map<?, ?> resp = client.post()
        .uri("/graphql")
        .body(payload)
        .retrieve()
        .body(Map.class);

    // Parse JSON
    Map<LocalDate, Integer> out = new HashMap<>();

    Object dataObj = resp.get("data");
    if (!(dataObj instanceof Map<?, ?> data)) return out;

    Object userObj = data.get("user");
    if (!(userObj instanceof Map<?, ?> user)) return out;

    Object ccObj = ((Map<?, ?>) user.get("contributionsCollection")).get("contributionCalendar");
    if (!(ccObj instanceof Map<?, ?> cc)) return out;

    Object weeksObj = cc.get("weeks");
    if (!(weeksObj instanceof List<?> weeks)) return out;

    for (Object w : weeks) {
      if (!(w instanceof Map<?, ?> wm)) continue;
      Object daysObj = wm.get("contributionDays");
      if (!(daysObj instanceof List<?> days)) continue;

      for (Object d : days) {
        if (!(d instanceof Map<?, ?> dm)) continue;
        String date = String.valueOf(dm.get("date"));
        int count = ((Number) dm.get("contributionCount")).intValue();
        out.put(LocalDate.parse(date), count);
      }
    }

    return out;
  }
}