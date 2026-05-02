const TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiI4MTQ3MjMxMDQxNDNAdHJwLnNybXRyaWNoeS5lZHUuaW4iLCJleHAiOjE3Nzc3MDM3OTQsImlhdCI6MTc3NzcwMjg5NCwiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6ImEyNzBlNmMyLTc2MTUtNDQyOS1iNzY3LWQ4MTI3Yjg1ZWY1YSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6InNoYWZlZWsgYWhtZWQiLCJzdWIiOiJiZWE0MjYyYS0xYjQ3LTRmYzYtOWVjNi04NDc1M2NjYTI2NGIifSwiZW1haWwiOiI4MTQ3MjMxMDQxNDNAdHJwLnNybXRyaWNoeS5lZHUuaW4iLCJuYW1lIjoic2hhZmVlayBhaG1lZCIsInJvbGxObyI6IjgxNDcyMzEwNDE0MyIsImFjY2Vzc0NvZGUiOiJRa2JweEgiLCJjbGllbnRJRCI6ImJlYTQyNjJhLTFiNDctNGZjNi05ZWM2LTg0NzUzY2NhMjY0YiIsImNsaWVudFNlY3JldCI6InB1V3JHSmpoUVdhV2NoaHMifQ.QZJW4KD7-R534c5d3x6TZikrbcHGcDGiLMfrmPfygb4"

async function Log(stack, level, pkg, message) {
  try {
    const response = await fetch(
      "http://20.207.122.201/evaluation-service/logs",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${TOKEN}`
        },
        body: JSON.stringify({
          stack: stack,
          level: level,
          package: pkg,
          message: message
        })
      }
    )
    const data = await response.json()
    return data
  } catch (error) {
    throw error
  }
}

module.exports = { Log }
