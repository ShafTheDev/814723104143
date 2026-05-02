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
