import gc
import asyncio
import framebuf
from machine import Pin, SoftSPI
import display_driver as ssd1306

# --- Константы анимации ---
WIDTH = 128
HEIGHT = 64
FRAME_SIZE = 1024  # (128 * 64 // 8) байт для SSD1306
FILE_NAME = "brain.bin"
FPS = 30

# Глобальный объект дисплея
oled = None

def init_display():
    """Инициализация OLED и оптимизация параметров под видеосъемку"""
    global oled
    try:
        # SoftSPI требует MISO, даже если он не используется физически
        spi = SoftSPI(
            baudrate=4000000,
            polarity=0,
            phase=0,
            sck=Pin(8),   # D0 (SCLK)
            mosi=Pin(9),  # D1 (MOSI)
            miso=Pin(3)   # Не подключен, нужен для инициализации SoftSPI
        )
        
        dc = Pin(11, Pin.OUT)
        cs = Pin(12, Pin.OUT)
        res = Pin(10, Pin.OUT)
        
        oled = ssd1306.SSD1306_SPI(WIDTH, HEIGHT, spi, dc, res, cs)

        # Тюнинг драйвера: убираем мерцание и пересвет для камеры
        oled.write_cmd(0xD5) # SET_DISP_CLK_DIV
        oled.write_cmd(0xF0) # Max refresh rate
        oled.write_cmd(0xD9) # SET_PRECHARGE
        oled.write_cmd(0xF1) 
        oled.contrast(150)   # Средняя яркость

        oled.fill(0)
        oled.text("System Ready", 0, 0)
        oled.show()
        print("✅ Display initialized")
        return True
    except Exception as e:
        print(f"⚠️ Display init failed: {e}")
        return False

async def display_task():
    """Асинхронный цикл проигрывания анимации"""
    global oled
    
    # Выделяем буфер один раз для экономии RAM
    buffer = bytearray(FRAME_SIZE)
    fb = framebuf.FrameBuffer(buffer, WIDTH, HEIGHT, framebuf.MONO_HLSB)
    
    while True:
        if oled:
            try:
                with open(FILE_NAME, "rb") as f:
                    while f.readinto(buffer) == FRAME_SIZE:
                        oled.blit(fb, 0, 0)
                        oled.show()
                        # Рассчитываем задержку исходя из FPS
                        await asyncio.sleep_ms(1000 // FPS)
            except Exception as e:
                print(f"Animation error: {e}")
                await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)

async def main():
    """Точка входа в систему"""
    # Инициализируем дисплей
    init_display()
    
    # Запускаем задачу анимации в фоне
    asyncio.create_task(display_task())

    print(f"✅ Система запущена. RAM free: {gc.mem_free()} bytes")
    
    # Основной бесконечный цикл
    while True:
        await asyncio.sleep(1)

# Запуск программы
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Остановлено пользователем")