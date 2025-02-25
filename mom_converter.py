# -*- coding: utf-8 -*-
# 将midi文件转化为moundofmusic数据
# pip install mido
# pip install Gooey

import mido
import csv
from gooey import Gooey,GooeyParser

# midi音高：moundofmusic音高，音域三个八度
DIC_NOTES = {48: 41, 49: -41, 50: 42, 51: -42, 52: 43, 53: 44, 54: -44, 55: 45, 56: -45, 57: 46, 58: -46, 59: 47, 60: 51, 61: -51, 62: 52, 63: -52, 64: 53, 65: 54, 66: -54, 67: 55, 68: -55, 69: 56, 70: -56, 71: 57, 72: 61, 73: -61, 74: 62, 75: -62, 76: 63, 77: 64, 78: -64, 79: 65, 80: -65, 81: 66, 82: -66, 83: 67}
DIC_NOTES_OUT = {21: 16, 22: -16, 23: 17, 24: 21, 25: -21, 26: 22, 27: -22, 28: 23, 29: 24, 30: -24, 31: 25, 32: -25, 33: 26, 34: -26, 35: 27, 36: 31, 37: -31, 38: 32, 39: -32, 40: 33, 41: 34, 42: -34, 43: 35, 44: -35, 45: 36, 46: -36, 47: 37, 84: 71, 85: -71, 86: 72, 87: -72, 88: 73, 89: 74, 90: -74, 91: 75, 92: -75, 93: 76, 94: -76, 95: 77, 96: 81, 97: -81, 98: 82, 99: -82, 100: 83, 101: 84, 102: -84, 103: 85, 104: -85, 105: 86, 106: -86, 107: 87, 108: 91}


def midi_to_mom(filename_midi=''):
    if not filename_midi.endswith('.mid'):
        print('Please select a midi file!')
        return
    # 读取MIDI文件
    midi_file = mido.MidiFile(filename_midi)
    # 获取MIDI文件的ticks_per_beat
    ticks_per_beat = midi_file.ticks_per_beat
    # 初始化tempo
    tempo = 1000000  # 默认tempo
    # 计算每个tick的时间（秒）
    tick_time = tempo / (ticks_per_beat * 1000000)
    # 确定输出文件名
    filename_csv = filename_midi.replace('.mid','.csv')
    # 准备CSV文件
    with open(filename_csv, 'w', newline='') as csvfile:
        count = 0
        result = []
        writer = csv.writer(csvfile)
        # 写入标题行
        writer.writerow(['id', 'pitch', 'time'])
        # 初始化变量
        total_time = 0.0
        notes_on = {}  # 存储音符的开始时间和音符号
        # 遍历MIDI文件中的每个轨道
        for track in midi_file.tracks:
            for msg in track:
                if msg.type == 'set_tempo': # 更新tick_time
                    tempo = msg.tempo
                    tick_time = tempo / (ticks_per_beat * 1000000)
                    # print(f'tempo change to: {tempo}')
                total_time += msg.time * tick_time  # 当前累积时间记录
                if msg.type == 'note_on' and msg.velocity > 0:  # 计算当前音符的开始时间
                    notes_on[msg.note] = total_time
                    count += 1
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):  # 计算当前音符的停止时间
                    if msg.note in notes_on:
                        play_time = notes_on[msg.note]
                        # 转化、记录数据
                        if (msg.note not in DIC_NOTES.keys()):
                            note = DIC_NOTES_OUT[msg.note]    # 超出音域的音符
                            print(f'WARNING! <id:{count} pitch:{note}> not in range, need to be transpose!')
                        else:
                            note = DIC_NOTES[msg.note]
                        result.append((count, note, play_time))
                        writer.writerow([count, note, round(play_time,3)])  # 时间只保留三位小数
    print(f'Successfully create midi data file: {filename_csv}')
    return midi_file, result

@Gooey(program_name='Mound of Music Data Converter',
       show_success_modal=False,
       show_restart_button=False,)
def main():
    parser = GooeyParser(description = 'Convert a midi file to Mound of Music data type.')
    parser.add_argument('filename_midi', help = 'Midi File with ONE track', widget = 'FileChooser')
    args = parser.parse_args()
    midi_to_mom(args.filename_midi)

if __name__ == '__main__':
    # midi_file, result = midi_to_mom(MIDI_FILE)
    main()