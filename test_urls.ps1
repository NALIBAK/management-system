$baseUrl = "http://localhost/management-system/Main/Frontend"
$pages = @(
    "login.html",
    "dashboard.html",
    "students/index.html",
    "staff/index.html",
    "departments/index.html",
    "courses/index.html",
    "timetable/index.html",
    "attendance/index.html",
    "marks/index.html",
    "fees/index.html",
    "reports/index.html",
    "notifications/index.html",
    "settings/index.html"
)

Write-Host "--- URL Connectivity Test ---"
foreach ($page in $pages) {
    $url = "$baseUrl/$page"
    try {
        $response = Invoke-WebRequest -Uri $url -Method Head -ErrorAction Stop
        Write-Host "SUCCESS: $page - Status $($response.StatusCode)" -ForegroundColor Green
    } catch {
        Write-Host "FAILED: $page - Error $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
             Write-Host "  Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Yellow
        }
    }
}
