"""
Advanced Features Handler
Handles news, weather, code analysis, GitHub, web automation, package management, etc.
"""

import os
import sys
import subprocess
import requests
from bs4 import BeautifulSoup
import feedparser
import schedule
from datetime import datetime as dt_datetime, timedelta
import ast

try:
    from git import Repo
    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")


class AdvancedFeatures:
    def __init__(self):
        pass
    
    def news_weather(self, type, location=None, category=None):
        """Get news and weather updates"""
        try:
            if type == "weather":
                if not WEATHER_API_KEY:
                    return {"status": "error", "message": "Weather API key not configured"}
                
                if not location:
                    location = "London"
                
                url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units=metric"
                response = requests.get(url)
                data = response.json()
                
                if response.status_code == 200:
                    weather = data['weather'][0]['description']
                    temp = data['main']['temp']
                    feels_like = data['main']['feels_like']
                    humidity = data['main']['humidity']
                    
                    message = f"Weather in {location}: {weather.capitalize()}, {temp}°C (feels like {feels_like}°C), Humidity: {humidity}%"
                    return {"status": "success", "message": message, "data": data}
                else:
                    return {"status": "error", "message": "Could not fetch weather data"}
            
            elif type == "news":
                if not NEWS_API_KEY:
                    feed_url = "https://feeds.bbci.co.uk/news/rss.xml"
                    feed = feedparser.parse(feed_url)
                    
                    headlines = []
                    for entry in feed.entries[:5]:
                        headlines.append(f"• {entry.title}")
                    
                    message = "Top Headlines:\n" + "\n".join(headlines)
                    return {"status": "success", "message": message}
                
                url = f"https://newsapi.org/v2/top-headlines?apiKey={NEWS_API_KEY}&country=us"
                if category:
                    url += f"&category={category}"
                
                response = requests.get(url)
                data = response.json()
                
                if response.status_code == 200:
                    articles = data['articles'][:5]
                    headlines = [f"• {article['title']}" for article in articles]
                    message = "Top Headlines:\n" + "\n".join(headlines)
                    return {"status": "success", "message": message, "data": articles}
                else:
                    return {"status": "error", "message": "Could not fetch news"}
            
            elif type == "briefing":
                weather_result = self.news_weather("weather", location)
                news_result = self.news_weather("news", category=category)
                
                briefing = f"Daily Briefing:\n\n{weather_result['message']}\n\n{news_result['message']}"
                return {"status": "success", "message": briefing}
            
            else:
                return {"status": "error", "message": "Invalid news/weather type"}
                
        except Exception as e:
            return {"status": "error", "message": f"News/weather failed: {str(e)}"}
    
    def code_analysis(self, operation, code_content=None, language=None, file_path=None):
        """Analyze and debug code"""
        try:
            if operation == "analyze":
                if file_path:
                    with open(file_path, 'r') as f:
                        code_content = f.read()
                
                if not code_content:
                    return {"status": "error", "message": "No code content provided"}
                
                if language == "python" or (file_path and file_path.endswith('.py')):
                    try:
                        ast.parse(code_content)
                        return {"status": "success", "message": "Code syntax is valid", "analysis": "No syntax errors found"}
                    except SyntaxError as e:
                        return {"status": "error", "message": f"Syntax error: {e.msg} at line {e.lineno}"}
                
                return {"status": "success", "message": "Basic analysis completed", "analysis": "Code structure looks acceptable"}
            
            elif operation == "debug":
                if not code_content:
                    return {"status": "error", "message": "No code content for debugging"}
                
                suggestions = []
                
                if "print(" in code_content and language == "python":
                    suggestions.append("Consider using logging instead of print statements for production code")
                
                if "except:" in code_content:
                    suggestions.append("Use specific exception types instead of bare except clauses")
                
                if len(code_content.split('\n')) > 100:
                    suggestions.append("Consider breaking large functions into smaller ones")
                
                message = "Debugging suggestions:\n• " + "\n• ".join(suggestions) if suggestions else "No obvious issues found"
                return {"status": "success", "message": message}
            
            elif operation == "write":
                if not code_content:
                    return {"status": "error", "message": "No code description provided"}
                
                return {"status": "success", "message": f"Code generation request: {code_content}", "suggestion": "Use the main AI model to generate specific code"}
            
            elif operation == "review":
                if file_path:
                    with open(file_path, 'r') as f:
                        code_content = f.read()
                
                if not code_content:
                    return {"status": "error", "message": "No code content to review"}
                
                lines = code_content.split('\n')
                review_points = []
                
                for i, line in enumerate(lines, 1):
                    if len(line) > 100:
                        review_points.append(f"Line {i}: Line too long ({len(line)} characters)")
                    if line.strip().startswith('TODO') or line.strip().startswith('FIXME'):
                        review_points.append(f"Line {i}: Unresolved TODO/FIXME comment")
                
                message = "Code Review:\n• " + "\n• ".join(review_points) if review_points else "Code looks good overall"
                return {"status": "success", "message": message}
            
            else:
                return {"status": "error", "message": "Invalid code analysis operation"}
                
        except Exception as e:
            return {"status": "error", "message": f"Code analysis failed: {str(e)}"}
    
    def github_operations(self, operation, repo_url=None, local_path=None, commit_message=None):
        """GitHub integration operations"""
        if not GIT_AVAILABLE:
            return {"status": "error", "message": "GitPython not installed"}
        
        try:
            if operation == "clone":
                if not repo_url or not local_path:
                    return {"status": "error", "message": "Repository URL and local path required"}
                
                Repo.clone_from(repo_url, local_path)
                return {"status": "success", "message": f"Cloned {repo_url} to {local_path}"}
            
            elif operation == "status":
                if not local_path:
                    local_path = "."
                
                repo = Repo(local_path)
                status = []
                
                if repo.is_dirty():
                    status.append("Working directory has uncommitted changes")
                    for item in repo.index.diff(None):
                        status.append(f"Modified: {item.a_path}")
                    for item in repo.untracked_files:
                        status.append(f"Untracked: {item}")
                else:
                    status.append("Working directory is clean")
                
                return {"status": "success", "message": "\n".join(status)}
            
            elif operation == "commit":
                if not local_path:
                    local_path = "."
                if not commit_message:
                    commit_message = "Auto commit via JARVIS"
                
                repo = Repo(local_path)
                repo.git.add(A=True)
                repo.index.commit(commit_message)
                
                return {"status": "success", "message": f"Committed changes: {commit_message}"}
            
            elif operation == "push":
                if not local_path:
                    local_path = "."
                
                repo = Repo(local_path)
                origin = repo.remote(name='origin')
                origin.push()
                
                return {"status": "success", "message": "Pushed changes to remote repository"}
            
            elif operation == "pull":
                if not local_path:
                    local_path = "."
                
                repo = Repo(local_path)
                origin = repo.remote(name='origin')
                origin.pull()
                
                return {"status": "success", "message": "Pulled latest changes from remote repository"}
            
            else:
                return {"status": "error", "message": "Invalid GitHub operation"}
                
        except Exception as e:
            return {"status": "error", "message": f"GitHub operation failed: {str(e)}"}
    
    def web_automation(self, operation, url, form_data=None, selector=None):
        """Web automation operations"""
        try:
            if operation == "scrape":
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                if selector:
                    elements = soup.select(selector)
                    data = [elem.get_text().strip() for elem in elements]
                else:
                    data = soup.get_text().strip()
                
                return {"status": "success", "message": f"Scraped data from {url}", "data": data}
            
            elif operation == "summarize":
                response = requests.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                for script in soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = ' '.join(chunk for chunk in chunks if chunk)
                
                summary = text[:500] + "..." if len(text) > 500 else text
                
                return {"status": "success", "message": f"Summary of {url}", "summary": summary}
            
            elif operation == "screenshot":
                if not SELENIUM_AVAILABLE:
                    return {"status": "error", "message": "Selenium not installed"}
                
                try:
                    options = Options()
                    options.add_argument('--headless')
                    driver = webdriver.Chrome(options=options)
                    driver.get(url)
                    
                    import time
                    screenshot_path = f"screenshot_{int(time.time())}.png"
                    driver.save_screenshot(screenshot_path)
                    driver.quit()
                    
                    return {"status": "success", "message": f"Screenshot saved to {screenshot_path}"}
                except Exception as e:
                    return {"status": "error", "message": f"Screenshot failed: {str(e)}"}
            
            elif operation == "fill_form":
                return {"status": "info", "message": "Form filling requires custom implementation for each site"}
            
            else:
                return {"status": "error", "message": "Invalid web automation operation"}
                
        except Exception as e:
            return {"status": "error", "message": f"Web automation failed: {str(e)}"}
    
    def package_manager(self, operation, package_type, package_name=None):
        """Manage software packages"""
        try:
            if package_type == "python":
                if operation == "install":
                    if not package_name:
                        return {"status": "error", "message": "Package name required"}
                    
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", package_name], 
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        return {"status": "success", "message": f"Installed Python package: {package_name}"}
                    else:
                        return {"status": "error", "message": f"Failed to install {package_name}: {result.stderr}"}
                
                elif operation == "update":
                    if package_name:
                        result = subprocess.run(
                            [sys.executable, "-m", "pip", "install", "--upgrade", package_name],
                            capture_output=True, text=True
                        )
                    else:
                        result = subprocess.run(
                            [sys.executable, "-m", "pip", "list", "--outdated"],
                            capture_output=True, text=True
                        )
                    
                    return {"status": "success", "message": f"Update result: {result.stdout}"}
                
                elif operation == "list":
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "list"], 
                        capture_output=True, text=True
                    )
                    return {"status": "success", "message": "Installed Python packages:", "data": result.stdout}
                
                elif operation == "uninstall":
                    if not package_name:
                        return {"status": "error", "message": "Package name required"}
                    
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "uninstall", "-y", package_name],
                        capture_output=True, text=True
                    )
                    
                    if result.returncode == 0:
                        return {"status": "success", "message": f"Uninstalled Python package: {package_name}"}
                    else:
                        return {"status": "error", "message": f"Failed to uninstall {package_name}"}
            
            else:
                return {"status": "error", "message": "Unsupported package type"}
                
        except Exception as e:
            return {"status": "error", "message": f"Package management failed: {str(e)}"}
    
    def task_scheduler(self, operation, task_name=None, datetime_str=None, message=None):
        """Schedule tasks and reminders"""
        try:
            if operation == "add":
                if not task_name or not datetime_str:
                    return {"status": "error", "message": "Task name and datetime required"}
                
                try:
                    task_datetime = dt_datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")
                    
                    def task_function():
                        print(f"\n🔔 REMINDER: {task_name}")
                        if message:
                            print(f"📝 {message}")
                    
                    schedule.every().day.at(task_datetime.strftime("%H:%M")).do(task_function).tag(task_name)
                    
                    return {"status": "success", "message": f"Scheduled task '{task_name}' for {datetime_str}"}
                
                except ValueError:
                    return {"status": "error", "message": "Invalid datetime format. Use YYYY-MM-DD HH:MM"}
            
            elif operation == "list":
                jobs = schedule.jobs
                if not jobs:
                    return {"status": "success", "message": "No scheduled tasks"}
                
                task_list = []
                for job in jobs:
                    task_list.append(f"• {job.tags} - Next run: {job.next_run}")
                
                return {"status": "success", "message": "Scheduled tasks:\n" + "\n".join(task_list)}
            
            elif operation == "remove":
                if not task_name:
                    return {"status": "error", "message": "Task name required"}
                
                schedule.clear(task_name)
                return {"status": "success", "message": f"Removed task '{task_name}'"}
            
            elif operation == "alarm":
                if not datetime_str:
                    return {"status": "error", "message": "Alarm time required"}
                
                try:
                    alarm_time = dt_datetime.strptime(datetime_str, "%H:%M").time()
                    
                    def alarm_function():
                        print("\n🚨 ALARM! ALARM! ALARM! 🚨")
                        if message:
                            print(f"📢 {message}")
                    
                    schedule.every().day.at(datetime_str).do(alarm_function).tag(f"alarm_{datetime_str}")
                    
                    return {"status": "success", "message": f"Set alarm for {datetime_str}"}
                
                except ValueError:
                    return {"status": "error", "message": "Invalid time format. Use HH:MM"}
            
            else:
                return {"status": "error", "message": "Invalid task scheduler operation"}
                
        except Exception as e:
            return {"status": "error", "message": f"Task scheduling failed: {str(e)}"}