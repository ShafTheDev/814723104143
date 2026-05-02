# Stage 1

## Core Actions Supported
- Fetch all notifications for a user
- Fetch a single notification by ID
- Mark a notification as read
- Mark all notifications as read
- Fetch unread notification count
- Stream real-time notifications

---

## API Endpoints

### 1. Get All Notifications
**GET** `/api/v1/notifications`

**Headers:**
| Key | Value |
|---|---|
| Content-Type | application/json |
| X-Student-ID | student_001 |

**Query Parameters:**
| Parameter | Type | Description |
|---|---|---|
| page | integer | Page number |
| limit | integer | Results per page |
| notification_type | string | "Event" or "Result" or "Placement" |

**Response (200 OK):**
```json
{
  "success": true,
  "page": 1,
  "limit": 10,
  "total": 50,
  "notifications": [
    {
      "id": "uuid",
      "type": "Placement",
      "message": "Google is hiring",
      "isRead": false,
      "createdAt": "2026-04-22T17:51:30Z"
    }
  ]
}
```

**Response (Internal Server Error):**
```json
{
  "success": false,
  "error": "Internal server error"
}
```

---

### 2. Get Single Notification
**GET** `/api/v1/notifications/:id`

**Headers:**
| Key | Value |
|---|---|
| Content-Type | application/json |
| X-Student-ID | student_001 |

**Response :**
```json
{
  "success": true,
  "notification": {
    "id": "uuid",
    "type": "Placement",
    "message": "Google is hiring",
    "isRead": false,
    "createdAt": "2026-04-22T17:51:30Z"
  }
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Notification not found"
}
```

---

### 3. Mark Single Notification as Read
**PATCH** `/api/v1/notifications/:id/read`

**Headers:**
| Key | Value |
|---|---|
| Content-Type | application/json |
| X-Student-ID | student_001 |

**Response:**
```json
{
  "success": true,
  "message": "Notification marked as read",
  "id": "uuid"
}
```

**Response (404 Not Found):**
```json
{
  "success": false,
  "error": "Notification not found"
}
```

---

### 4. Mark All Notifications as Read
**PATCH** `/api/v1/notifications/read-all`

**Headers:**
| Key | Value |
|---|---|
| Content-Type | application/json |
| X-Student-ID | student_001 |

**Response:**
```json
{
  "success": true,
  "message": "All notifications marked as read"
}
```

---

### 5. Get Unread Notification Count
**GET** `/api/v1/notifications/unread/count`

**Headers:**
| Key | Value |
|---|---|
| Content-Type | application/json |
| X-Student-ID | student_001 |

**Response:**
```json
{
  "success": true,
  "unreadCount": 12
}
```

---

## Real-Time Notification Mechanism:

**GET** `/api/v1/notifications/stream`

**Why SSE over WebSockets?**
- Notifications are one-directional so the server pushes to client only
- No need for client to send data back to server as it is one-directinal 
- Easier to implement 
- Automatically reconnects if connection drops or fails

**How It Works:**
1. Frontend opens a persistent connection to `/api/v1/notifications/stream`
2. Server keeps the connection alive
3. When a new notification arrives, server sends it immediately 
4. When Frontend receives the event it updates UI without page reload

**Headers:**
| Key | Value |
|---|---|
| Content-Type | text/event-stream |
| X-Student-ID | student_001 |

**Event Format:**
data: {"id": "uuid", "type": "Placement", "message": "Google is hiring", "createdAt": "2026-04-22T17:51:30Z"}

---

## JSON Schema — Notification Object

| Field | Type | Required | Description |
|---|---|---|---|
| id | string (UUID) | Yes | Unique notification ID |
| type | string (enum) | Yes | "Event", "Result", "Placement" |
| message | string | Yes | Notification content |
| isRead | boolean | Yes | Read status of notification |
| createdAt | string (ISO 8601) | Yes | Creation timestamp |

---

# Stage 2

## Database — MySQL

**Why MySQL:**
- Widely used in production applications
- Notifications and students for a relational model 
- Relational database fits perfectly 
- Supports ENUM types natively (Event/Result/Placement)
- ACID compliant — no data loss on failures
- Easy to set up and well documented

---

## Database Schema

**Students Table:**
```sql
CREATE TABLE students (
  id VARCHAR(20) PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) UNIQUE NOT NULL
);
```

**Notifications Table:**
```sql
CREATE TABLE notifications (
  id VARCHAR(20) PRIMARY KEY,
  student_id VARCHAR(20) NOT NULL,
  type ENUM('Event', 'Result', 'Placement') NOT NULL,
  message TEXT NOT NULL,
  isRead BOOLEAN DEFAULT false,
  createdAt TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (student_id) REFERENCES students(id)
);
```

---

## Scaling Problems as Data Grows

1. **Full table scans** — querying millions of contents in the table slows the process
2. **No pagination** — returning all notifications overfloods the server
3. **Single DB server** — single database server becomes a bottleneck under higher load
4. **Unread count queries** — counting unread on every page load is expensive
5. **Old data buildup** — notifications table keeps growing with no archiving

---

## Solutions

- Add indexes on frequently queried columns for easier acessing 
- using pagination to avoid overflood situations
- Use read replicas to lower the load on main data base 
- Cache unread counts in Redis instead of scanning the whole table for unread count
- Archive notifications older than 6 months to a separate table to maintain main table 

---

## SQL Queries

**Get all notifications for a student:**
```sql
SELECT * FROM notifications
WHERE student_id = 'uuid'
ORDER BY createdAt DESC
LIMIT 10 OFFSET 0;
```

**Get unread notifications:**
```sql
SELECT * FROM notifications
WHERE student_id = 'uuid'
AND isRead = false
ORDER BY createdAt DESC;
LIMIT 10 OFFSET 0;
```

**Mark single notification as read:**
```sql
UPDATE notifications
SET isRead = true
WHERE id = 'uuid';
```

**Mark all as read:**
```sql
UPDATE notifications
SET isRead = true
WHERE student_id = 'uuid';
```

**Get unread count:**
```sql
SELECT COUNT(*) as unreadCount
FROM notifications
WHERE student_id = 'uuid'
AND isRead = false;
```

**Get notifications by type:**
```sql
SELECT * FROM notifications
WHERE student_id = 'uuid'
AND type = 'Placement'
ORDER BY createdAt DESC;
LIMIT 10 OFFSET 0;
```
---

# Stage 3

## Query Analysis

**Old Query:**
```sql
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt ASC;
```

---

## Is This Query Accurate?
This query is logically correct but it has issues
- `SELECT *` is used to fetch all the data which is not necessary
- No indexes which reads every single row in the table
- No `LIMIT` — could return thousands of rows at once

---

## Why Is It Slow?
- No indexes therefore reads every single row making it slower
- A full table scan is done with each call making it slower for the output
- `ORDER BY` then orders the gathered data in ascending which is already in huge amount

---

## New Query
```sql
SELECT id, type, message, isRead, createdAt
FROM notifications
WHERE student_id = 1042
AND isRead = false
ORDER BY createdAt ASC
LIMIT 20 OFFSET 0;
```
---

## Should We Index Every Column?
NO we do not need to index every column 
- indexing every column slows down the process
- we only need to index required columns

---

## Computation Cost
- **old query:** - full scan of 5,000,000 rows
- **new query:** - directly jumps to matching rows

---

## Query — Students Who Got Placement Notification in Last 7 Days
```sql
SELECT DISTINCT student_id
FROM notifications
WHERE type = 'Placement'
AND createdAt >= NOW() - INTERVAL 7 DAY;
```
---

# Stage 4

## Problem
Notifications are fetched on every page load for every student, overwhelming the database and causing poor user experience.

---

## Solutions & Tradeoffs

### 1. Caching with Redis
Storing the result in redis instead of hitting the database all the time
- reduces DB load
- Very fast response times
- it can be scaled if needed
 
### it can stale the data and needs extra infrastructure to manage it 
---

### 2. Pagination
Never load all notifications at once. Load 10-20 at a time
- reduce the data transfered during queries
- lighter db queries
---

### 3. Database Indexing
Add indexes on frequently queried columns.
- faster query execution
- no need of extra infrastructure

### but requires careful planning for implementation
---

### 4. Read Replicas
Route all read queries to replica database
- distributes db load with replica database
### Only handles the read queries not the write queries as it is a replica database
---

# Stage 5

## Problem with Current Implementation

**Current pseudocode:**
```
function notify_all(student_ids: array, message: string):
  for student_id in student_ids:
    send_email(student_id, message)
    save_to_db(student_id, message)
    push_to_app(student_id, message)
```

---

## Shortcomings
1. processes one student at a time, 50,000 students will take very long
2. if email sent fails the whole flow breaks
3. email, DB save and push all happen together
4. failed notifications are not restarted

---

## What Happens When send_email Fails for 200 Students Midway?
- Those 200 students will not recevie the mail 
- No record of these 200 students
- missing of the record of these 200 students

---

## Should DB Save and Email Happen Together?
No they should no happend together 
- if they happen together and the email fails then the notification sent is not saved and the data is lost
- so always save the data in the database and then send the email 
---

## Redesigned Solution

**revised psudocode**
```
function notify_all(student_ids, message):

    for each student_id in student_ids:
        save_to_db(student_id, message)
        add_to_email_queue(student_id, message)
        add_to_push_queue(student_id, message)


function email_worker():

    loop forever:
        job = get_next_email_job()
        if job exists:
            try:
                send_email(job.student_id, job.message)
            catch:
                retry_email_job(job)


function push_worker():

    loop forever:
        job = get_next_push_job()
        if job exists:
            try:
                send_push(job.student_id, job.message)
            catch:
                retry_push_job(job)
```

---
# Stage 6

<img width="1240" height="77" alt="Screenshot 2026-05-02 130722" src="https://github.com/user-attachments/assets/487f3e3c-63a1-45d1-91ad-57c8bb8f8fb4" />
