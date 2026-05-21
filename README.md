# Concert Ticket Database App

Flask and PostgreSQL web application for managing concert ticket sales, artist schedules, customer purchases, and venue revenue analytics.

## Project Overview

This project is a database-backed web application designed for a small concert ticketing business. It allows users to manage artists, venues, concerts, customers, ticket purchases, and revenue-related reports.

The app combines database design, SQL queries, backend development, and a simple web interface to support practical business operations and analytics.

## Business Use Case

A concert ticketing business needs to track events, customers, purchases, venues, and revenue. This application provides a centralized system for managing that information while also generating useful analytics for decision-making.

Example business questions include:

- Which artists generate the most revenue?
- Which venues are performing best?
- Which customers have spent the most?
- Which concerts are available in a given city?
- How can ticket sales activity be summarized for reporting?

## Features

- Add and manage artists
- Add and manage venues
- Add and manage concerts
- Add and manage customers
- Record ticket purchases
- View customer spending summaries
- Rank artists by revenue
- Analyze venue performance
- Filter concerts by location
- Generate SQL-backed business reports

## Tools

Python · Flask · PostgreSQL · SQL · HTML/CSS · Render · Database Design

## Database Concepts Demonstrated

- Relational schema design
- Primary and foreign keys
- SQL joins
- Aggregate queries
- Revenue reporting
- Customer purchase history
- Web application integration with a PostgreSQL database

## Repository Structure

```text
concert-ticket-app/
├── app.py
├── templates/
├── static/
├── schema.sql
├── requirements.txt
├── README.md
└── render.yaml
