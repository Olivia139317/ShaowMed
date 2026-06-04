param(
  [string]$BaseUrl = "http://localhost:5000"
)

$ErrorActionPreference = "Stop"

function Invoke-Json {
  param(
    [string]$Method = "GET",
    [string]$Path,
    [object]$Body = $null
  )

  $Uri = "$BaseUrl$Path"
  if ($Body -ne $null) {
    $Json = $Body | ConvertTo-Json -Depth 8
    return Invoke-RestMethod -Uri $Uri -Method $Method -ContentType "application/json; charset=utf-8" -Body $Json -TimeoutSec 10
  }
  return Invoke-RestMethod -Uri $Uri -Method $Method -TimeoutSec 10
}

Write-Host "ShadowMe smoke test: $BaseUrl"

$health = Invoke-Json -Path "/health"
if ($health.status -ne "healthy") { throw "Health check failed." }
Write-Host "[OK] health version=$($health.version), restaurants=$($health.restaurant_count)"

$chat = Invoke-Json -Method "POST" -Path "/api/chat" -Body @{ message = "weekend friends recommendation" }
if (-not $chat.success -or -not $chat.data.identity_mode) { throw "Chat endpoint failed." }
Write-Host "[OK] chat identity=$($chat.data.identity_mode), restaurants=$($chat.data.recommendations.Count), activities=$($chat.data.activities.Count)"

$monitor = Invoke-Json -Method "POST" -Path "/api/queue-monitor/start" -Body @{ restaurant_name = "demo-restaurant"; target_count = 5 }
if (-not $monitor.success -or -not $monitor.data.task_id) { throw "Queue monitor start failed." }
Write-Host "[OK] queue monitor task=$($monitor.data.task_id)"

$allMonitors = Invoke-Json -Path "/api/monitors/check-all"
if (-not $allMonitors.success) { throw "Monitor check-all failed." }
Write-Host "[OK] monitors active=$($allMonitors.data.active_monitors), triggered=$($allMonitors.data.any_triggered)"

$ride = Invoke-Json -Method "POST" -Path "/api/ride-hailing" -Body @{ origin = "current location"; destination = "demo destination"; car_type = "express" }
if (-not $ride.success -or $ride.data.status -ne "success") { throw "Ride-hailing endpoint failed." }
Write-Host "[OK] ride wait=$($ride.data.driver_info.wait_time_minutes)min, price=$($ride.data.estimated_price)"

$proactive = Invoke-Json -Method "POST" -Path "/api/proactive-check" -Body @{ hour = 2; weekday = 2 }
if ($proactive.data.reason -ne "quiet_hours") { throw "Quiet-hours proactive check failed." }
Write-Host "[OK] proactive quiet_hours"

$busy = Invoke-Json -Method "POST" -Path "/api/proactive-check" -Body @{ hour = 12; weekday = 2; identity_mode = "rescue" }
if ($busy.data.reason -ne "user_busy") { throw "Busy proactive check failed." }
Write-Host "[OK] proactive user_busy"

$feedback = Invoke-Json -Method "POST" -Path "/api/proactive-feedback" -Body @{ action = "reject" }
if (-not $feedback.data.recorded) { throw "Proactive feedback failed." }
Write-Host "[OK] proactive feedback cooldown=$($feedback.data.cooldown_hours)h"

$sandbox = Invoke-Json -Path "/api/sandbox/status"
if (-not $sandbox.success -or $sandbox.data.restaurant_count -lt 3) { throw "Sandbox status failed." }
Write-Host "[OK] sandbox restaurants=$($sandbox.data.restaurant_count), activities=$($sandbox.data.activity_count), events=$($sandbox.data.recent_events.Count)"

Write-Host "Smoke test passed."
