#!/usr/bin/env python3
"""
Скрипт для быстрого тестирования всех сервисов CRM_college
Использование: python scripts/test_services.py
"""

import asyncio
import httpx
import json
import sys
from typing import Dict, Any
import time

# Конфигурация сервисов
SERVICES = {
    "auth": {
        "url": "http://localhost:8002",
        "name": "Auth Service",
        "health": "/api/auth/health"
    },
    "schedule": {
        "url": "http://localhost:8000", 
        "name": "Schedule Service",
        "health": "/api/schedule/health"
    },
    "techcard": {
        "url": "http://localhost:8001",
        "name": "Techcard Service",
        "health": "/api/techcard/health"
    }
}

class ServiceTester:
    def __init__(self):
        self.results = {}
        self.auth_token = None
        
    async def test_health_endpoint(self, service_name: str, base_url: str) -> Dict[str, Any]:
        """Тестирует health endpoint сервиса"""
        try:
            health_path = SERVICES[service_name].get("health", "/api/health")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{base_url}{health_path}")
                
                return {
                    "status": "✅ OK" if response.status_code == 200 else "❌ FAIL",
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds(),
                    "data": response.json() if response.status_code == 200 else None,
                    "error": None
                }
        except Exception as e:
            return {
                "status": "❌ ERROR",
                "status_code": None,
                "response_time": None,
                "data": None,
                "error": str(e)
            }
    
    async def test_auth_service(self) -> Dict[str, Any]:
        """Тестирует функциональность auth сервиса"""
        base_url = SERVICES["auth"]["url"]
        results = {}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Тест регистрации
                test_user = {
                    "email": f"test_{int(time.time())}@example.com",
                    "password": "testpassword123",
                    "full_name": "Test User"
                }
                
                register_response = await client.post(
                    f"{base_url}/api/auth/register",
                    json=test_user
                )
                
                results["register"] = {
                    "status": "✅ OK" if register_response.status_code in [200, 201] else "❌ FAIL",
                    "status_code": register_response.status_code,
                    "has_token": "access_token" in register_response.text if register_response.status_code in [200, 201] else False
                }
                
                # Тест логина
                login_data = {
                    "email": test_user["email"],
                    "password": test_user["password"]
                }
                
                login_response = await client.post(
                    f"{base_url}/api/auth/login",
                    json=login_data
                )
                
                results["login"] = {
                    "status": "✅ OK" if login_response.status_code == 200 else "❌ FAIL",
                    "status_code": login_response.status_code,
                    "has_token": False
                }
                
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    if "access_token" in login_data:
                        self.auth_token = login_data["access_token"]
                        results["login"]["has_token"] = True
                
                # Тест получения профиля (если есть токен)
                if self.auth_token:
                    profile_response = await client.get(
                        f"{base_url}/api/auth/me",
                        headers={"Authorization": f"Bearer {self.auth_token}"}
                    )
                    
                    results["profile"] = {
                        "status": "✅ OK" if profile_response.status_code == 200 else "❌ FAIL",
                        "status_code": profile_response.status_code
                    }
                
        except Exception as e:
            results["error"] = str(e)
            
        return results
    
    async def test_schedule_service(self) -> Dict[str, Any]:
        """Тестирует функциональность schedule сервиса"""
        base_url = SERVICES["schedule"]["url"]
        results = {}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Тест получения групп
                groups_response = await client.get(f"{base_url}/api/schedule/groups/")
                results["get_groups"] = {
                    "status": "✅ OK" if groups_response.status_code == 200 else "❌ FAIL",
                    "status_code": groups_response.status_code
                }
                
                # Тест получения расписания
                schedule_response = await client.get(f"{base_url}/api/schedule/list")
                results["get_schedule"] = {
                    "status": "✅ OK" if schedule_response.status_code == 200 else "❌ FAIL",
                    "status_code": schedule_response.status_code
                }
                
                # Тест получения аудиторий
                auditoriums_response = await client.get(f"{base_url}/api/schedule/auditoriums/")
                results["get_auditoriums"] = {
                    "status": "✅ OK" if auditoriums_response.status_code == 200 else "❌ FAIL",
                    "status_code": auditoriums_response.status_code
                }
                
        except Exception as e:
            results["error"] = str(e)
            
        return results
    
    async def test_techcard_service(self) -> Dict[str, Any]:
        """Тестирует функциональность techcard сервиса"""
        base_url = SERVICES["techcard"]["url"]
        results = {}
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Тест корневого endpoint
                root_response = await client.get(f"{base_url}/")
                results["root"] = {
                    "status": "✅ OK" if root_response.status_code == 200 else "❌ FAIL",
                    "status_code": root_response.status_code
                }
                
                # Тест получения техкарт (требует авторизации — проверяем доступность)
                try:
                    techcards_response = await client.get(f"{base_url}/api/techcards")
                    results["techcards_endpoint"] = {
                        "status": "✅ OK" if techcards_response.status_code in [200, 401, 403, 503] else "❌ FAIL",
                        "status_code": techcards_response.status_code
                    }
                except Exception:
                    results["techcards_endpoint"] = {
                        "status": "⚠️ ENDPOINT NOT FOUND",
                        "status_code": None
                    }
                
        except Exception as e:
            results["error"] = str(e)
            
        return results
    
    async def run_all_tests(self):
        """Запускает все тесты"""
        print("🧪 Запуск тестирования сервисов CRM_college...")
        print("=" * 60)
        
        # Тестируем health endpoints
        print("\n📊 Тестирование Health Endpoints:")
        for service_name, config in SERVICES.items():
            print(f"\n🔍 {config['name']} ({config['url']}):")
            result = await self.test_health_endpoint(service_name, config["url"])
            
            print(f"  Status: {result['status']}")
            print(f"  HTTP Code: {result['status_code']}")
            if result['response_time']:
                print(f"  Response Time: {result['response_time']:.3f}s")
            if result['error']:
                print(f"  Error: {result['error']}")
            
            self.results[f"{service_name}_health"] = result
        
        # Функциональные тесты
        print("\n🔧 Функциональные тесты:")
        
        # Auth сервис
        print(f"\n🔐 {SERVICES['auth']['name']}:")
        auth_results = await self.test_auth_service()
        for test_name, result in auth_results.items():
            if test_name != "error":
                print(f"  {test_name}: {result['status']} (HTTP {result['status_code']})")
        if "error" in auth_results:
            print(f"  Error: {auth_results['error']}")
        
        # Schedule сервис
        print(f"\n📅 {SERVICES['schedule']['name']}:")
        schedule_results = await self.test_schedule_service()
        for test_name, result in schedule_results.items():
            if test_name != "error":
                print(f"  {test_name}: {result['status']} (HTTP {result['status_code']})")
        if "error" in schedule_results:
            print(f"  Error: {schedule_results['error']}")
        
        # Techcard сервис
        print(f"\n📋 {SERVICES['techcard']['name']}:")
        techcard_results = await self.test_techcard_service()
        for test_name, result in techcard_results.items():
            if test_name != "error":
                print(f"  {test_name}: {result['status']} (HTTP {result['status_code']})")
        if "error" in techcard_results:
            print(f"  Error: {techcard_results['error']}")
        
        # Итоговый отчет
        print("\n" + "=" * 60)
        print("📋 ИТОГОВЫЙ ОТЧЕТ:")
        
        total_tests = 0
        passed_tests = 0
        
        for service_name, config in SERVICES.items():
            health_result = self.results.get(f"{service_name}_health", {})
            status = "🟢 РАБОТАЕТ" if health_result.get("status") == "✅ OK" else "🔴 НЕ РАБОТАЕТ"
            print(f"  {config['name']}: {status}")
            
            total_tests += 1
            if health_result.get("status") == "✅ OK":
                passed_tests += 1
        
        print(f"\nПройдено тестов: {passed_tests}/{total_tests}")
        
        if passed_tests == total_tests:
            print("🎉 Все сервисы работают корректно!")
            return 0
        else:
            print("⚠️ Некоторые сервисы имеют проблемы.")
            return 1

async def main():
    """Главная функция"""
    tester = ServiceTester()
    exit_code = await tester.run_all_tests()
    sys.exit(exit_code)

if __name__ == "__main__":
    asyncio.run(main())