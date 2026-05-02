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
