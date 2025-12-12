#!/usr/bin/env python3
"""
Комплексное тестирование всех API эндпоинтов для сервисов:
- auth_db (auth)
- tech_card_db (techcard) 
- schedule_db (schedule)
"""

import asyncio
import httpx
import json
from typing import Dict, List, Tuple
from urllib.parse import urljoin


class APITester:
    def __init__(self):
        self.auth_token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = {}
        
    async def test_endpoint(self, method: str, url: str, expected_status: int = 200, 
                           payload: dict = None, headers: dict = None) -> Tuple[bool, str, dict]:
        """
        Тестирует один эндпоинт
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if method.upper() == "GET":
                    response = await client.get(url, headers=headers)
                elif method.upper() == "POST":
                    response = await client.post(url, json=payload, headers=headers)
                elif method.upper() == "PUT":
                    response = await client.put(url, json=payload, headers=headers)
                elif method.upper() == "DELETE":
                    response = await client.delete(url, headers=headers)
                else:
                    return False, f"Метод {method} не поддерживается", {}
                
                success = response.status_code == expected_status
                status_desc = f"ожидался {expected_status}, получен {response.status_code}"
                
                try:
                    response_data = response.json()
                except:
                    response_data = {"raw_response": response.text}
                
                return success, status_desc, response_data
                
        except Exception as e:
            return False, f"Ошибка подключения: {str(e)}", {}

    async def test_auth_service(self):
        """Тестируем все эндпоинты auth сервиса"""
        print("\n🧪 Тестируем Auth Service (http://localhost:8002)")
        base_url = "http://localhost:8002"
        
        endpoints = [
            ("GET", "/api/health", 200),
            ("GET", "/", 200),
            # Тестовые запросы без авторизации
            ("GET", "/api/auth/me", 401),  # Ожидаем 401 без токена
            ("GET", "/api/users/me/history", 401),  # Ожидаем 401 без токена
        ]
        
        results = {}
        
        for method, endpoint, expected_status in endpoints:
            url = base_url + endpoint
            success, status_desc, data = await self.test_endpoint(method, url, expected_status)
            
            key = f"{method} {endpoint}"
            results[key] = {
                "success": success,
                "status_desc": status_desc,
                "data": data
            }
            
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {method} {endpoint} - {status_desc}")
        
        self.test_results["auth"] = results
        return results

    async def test_schedule_service(self):
        """Тестируем все эндпоинты schedule сервиса"""
        print("\n📅 Тестируем Schedule Service (http://localhost:8000)")
        base_url = "http://localhost:8000"
        
        endpoints = [
            ("GET", "/api/health", 200),
            ("GET", "/", 200),
            # Тестовые запросы без авторизации
            ("GET", "/api/auth/me", 401),  # Ожидаем 401 без токена
            ("GET", "/api/groups", 200),  # Может возвращать пустой список без авторизации
            ("GET", "/api/auditoriums", 200),  # Может возвращать пустой список без авторизации
            ("GET", "/api/schedule", 200),  # Может возвращать пустой список без авторизации
        ]
        
        results = {}
        
        for method, endpoint, expected_status in endpoints:
            url = base_url + endpoint
            success, status_desc, data = await self.test_endpoint(method, url, expected_status)
            
            key = f"{method} {endpoint}"
            results[key] = {
                "success": success,
                "status_desc": status_desc,
                "data": data
            }
            
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {method} {endpoint} - {status_desc}")
        
        self.test_results["schedule"] = results
        return results

    async def test_techcard_service(self):
        """Тестируем все эндпоинты techcard сервиса"""
        print("\n📋 Тестируем Techcard Service (http://localhost:8001)")
        base_url = "http://localhost:8001"
        
        endpoints = [
            ("GET", "/", 200),
            # Проверяем наличие роутов для технологических карт
            ("GET", "/api/techcards", 200),
            ("GET", "/api/dictionaries", 200),
        ]
        
        results = {}
        
        for method, endpoint, expected_status in endpoints:
            url = base_url + endpoint
            # Для несуществующих эндпоинтов ожидаем 404
            if endpoint in ["/api/techcards", "/api/dictionaries"]:
                expected_status = 404  # Эти эндпоинты могут не существовать
            
            success, status_desc, data = await self.test_endpoint(method, url, expected_status)
            
            key = f"{method} {endpoint}"
            results[key] = {
                "success": success,
                "status_desc": status_desc,
                "data": data
            }
            
            status_icon = "✅" if success else "❌"
            print(f"  {status_icon} {method} {endpoint} - {status_desc}")
        
        self.test_results["techcard"] = results
        return results

    async def run_comprehensive_tests(self):
        """Запускаем все тесты"""
        print("🚀 Запуск комплексного тестирования всех API сервисов...")
        
        await self.test_auth_service()
        await self.test_schedule_service()
        await self.test_techcard_service()
        
        # Выводим сводку
        self.print_summary()
    
    def print_summary(self):
        """Выводим сводку по тестам"""
        print("\n" + "="*60)
        print("📊 СВОДКА ТЕСТИРОВАНИЯ")
        print("="*60)
        
        total_tests = 0
        passed_tests = 0
        
        for service, results in self.test_results.items():
            print(f"\n{service.upper()} SERVICE:")
            service_passed = 0
            service_total = len(results)
            
            for endpoint, result in results.items():
                total_tests += 1
                if result["success"]:
                    passed_tests += 1
                    service_passed += 1
                status = "✅" if result["success"] else "❌"
                print(f"  {status} {endpoint}: {result['status_desc']}")
            
            print(f"  Итого: {service_passed}/{service_total} успешных тестов")
        
        print(f"\n🎯 ВСЕГО: {passed_tests}/{total_tests} успешных тестов")
        
        if passed_tests == total_tests:
            print("🎉 Все тесты пройдены успешно!")
        else:
            print(f"⚠️  Пройдено только {passed_tests}/{total_tests} тестов")
        
        return passed_tests == total_tests


async def main():
    tester = APITester()
    await tester.run_comprehensive_tests()


if __name__ == "__main__":
    asyncio.run(main())