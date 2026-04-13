import os
from PIL import Image

# Настройки
SOURCE_DIR = 'frames'        # Папка с вашими PNG (отрендеренными в 128x64)
OUTPUT_FILE = 'brain.bin'    # Имя выходного файла для загрузки на OLED
WIDTH = 128
HEIGHT = 64

def process_images():
    # Получаем список файлов и сортируем их (по именам: 001.png, ...)
    files = sorted([f for f in os.listdir(SOURCE_DIR) if f.endswith('.png')])
    
    if not files:
        print("В папке нет PNG файлов!")
        return

    all_frames_data = bytearray()

    for filename in files:
        path = os.path.join(SOURCE_DIR, filename)
        
        # Открываем, меняем размер (на всякий случай) и переводим в Ч/Б
        with Image.open(path) as img:
            img = img.resize((WIDTH, HEIGHT)).convert('L')

            # Все, что темнее значения 50 (из 255), станет абсолютно черным (0)
            # threshold = 50 
            # img = img.point(lambda p: p if p > threshold else 0)


            # --- УБИРАЕМ СЕТКУ ТОЧЕК НА БЕЛОМ ---
            # Все, что ярче 200 (из 255), станет идеально белым (255).
            # Это создаст "островки" чистого белого без черных точек.
            img = img.point(lambda p: 255 if p > 125 else (0 if p < 50 else p))
            # ------------------------------------

            
            # Дизеринг Floyd-Steinberg превращает "мыло" в четкие точки
            img_mono = img.convert('1', dither=Image.FLOYDSTEINBERG)
            
            # Конвертируем в байты (формат MONO_HLSB для SSD1306)
            # В Pillow формат '1' уже соответствует MONO_HLSB
            all_frames_data.extend(img_mono.tobytes())
            
        print(f"Обработан кадр: {filename}")

    # Сохраняем всё в один бинарник
    with open(OUTPUT_FILE, 'wb') as f:
        f.write(all_frames_data)
    
    print(f"\nГотово! Создан файл {OUTPUT_FILE}")
    print(f"Всего кадров: {len(files)}")
    print(f"Размер файла: {len(all_frames_data)} байт")

if __name__ == "__main__":
    process_images()
