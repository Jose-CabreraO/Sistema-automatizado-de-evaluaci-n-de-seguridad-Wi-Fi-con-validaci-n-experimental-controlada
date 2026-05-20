import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluador import calcular_wss, clasificar_riesgo

class TestWirelessSeverityScore(unittest.TestCase):

    def test_escenarios_experimento_tesis(self):
        """Valida los escenarios E1 a E5 definidos en la tesis"""
        
        escenarios = [
            # E1: WPA3 + AES → Bajo
            {"ssid": "E1_WPA3_AES", "auth": "WPA3-Personal", "cipher": "CCMP/AES", "signal": 85, "esperado": "BAJO"},
            # E2: WPA2 + AES → Medio
            {"ssid": "E2_WPA2_AES", "auth": "WPA2-Personal", "cipher": "CCMP/AES", "signal": 70, "esperado": "MEDIO"},
            # E3: WPA2 + TKIP → Alto
            {"ssid": "E3_WPA2_TKIP", "auth": "WPA2-Personal", "cipher": "TKIP", "signal": 75, "esperado": "ALTO"},
            # E4: WEP → Crítico
            {"ssid": "E4_WEP", "auth": "WEP", "cipher": "WEP", "signal": 60, "esperado": "CRÍTICO"},
            # E5: Open → Crítico
            {"ssid": "E5_OPEN", "auth": "Open", "cipher": "NONE", "signal": 90, "esperado": "CRÍTICO"},
        ]

        for esc in escenarios:
            with self.subTest(escenario=esc["ssid"]):
                resultado = calcular_wss(esc["auth"], esc["cipher"], esc["signal"])
                
                print(f"\n{esc['ssid']}: Score = {resultado['puntaje_final']} → {resultado['nivel_riesgo']}")
                
                self.assertLessEqual(resultado['puntaje_final'], 10.0)
                self.assertGreaterEqual(resultado['puntaje_final'], 0.0)
                
                # Verificar comportamiento monotónico (más inseguro = mayor score)
                if "E1" in esc["ssid"]:
                    self.assertLess(resultado['puntaje_final'], 3.0)
                elif "E5" in esc["ssid"] or "E4" in esc["ssid"]:
                    self.assertGreaterEqual(resultado['puntaje_final'], 7.0)

    def test_monotonicidad(self):
        """Verifica que al degradar la seguridad el score aumente"""
        # Misma señal, degradando configuración
        score_wpa3 = calcular_wss("WPA3-Personal", "CCMP/AES", 80)['puntaje_final']
        score_wpa2 = calcular_wss("WPA2-Personal", "CCMP/AES", 80)['puntaje_final']
        score_open = calcular_wss("Open", "NONE", 80)['puntaje_final']
        
        self.assertLess(score_wpa3, score_wpa2)
        self.assertLess(score_wpa2, score_open)

if __name__ == '__main__':
    unittest.main(verbosity=2)