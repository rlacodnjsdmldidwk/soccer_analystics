import numpy as np
import matplotlib.pyplot as plt

def draw_heatmap(data_imported, team_name, type):
    # 축구장 크기 (m)
    field_x = 120  # 가로
    field_y = 80  # 세로

    # 구간 크기 (가로 12개, 세로 8개)
    num_bins_x = 12
    num_bins_y = 8
    bin_x = field_x / num_bins_x
    bin_y = field_y / num_bins_y

    # 예시 패스 데이터 (x, y 좌표)
    passes = data_imported

    # 히트맵을 위한 2D 배열 (패스 개수를 카운트)
    heatmap = np.zeros((num_bins_y, num_bins_x))

    # 패스를 각 구간에 분류하고 개수 카운트
    for x, y in passes:
        # 가로 (x) 위치
        bin_x_index = min(int(x // bin_x), num_bins_x - 1)
        
        # 세로 (y) 위치
        bin_y_index = min(int(y // bin_y), num_bins_y - 1)
        
        # 해당 구간의 패스 개수 증가
        heatmap[bin_y_index, bin_x_index] += 1

    # 축구장 그림 그리기
    fig, ax = plt.subplots(figsize=(12, 8))

    # 축구장 외곽선
    ax.plot([0, 0, field_x, field_x, 0], [0, field_y, field_y, 0, 0], color="black")

    # 센터 라인
    ax.plot([field_x / 2, field_x / 2], [0, field_y], color="black")

    # 센터 서클
    center_circle = plt.Circle((field_x / 2, field_y / 2), 9.15, color="black", fill=False)
    ax.add_patch(center_circle)
    ax.scatter(field_x / 2, field_y / 2, color="black", s=20)  # 센터 스팟

    # 페널티 구역
    ax.plot([0, 16.5, 16.5, 0], [(field_y - 40.3) / 2, (field_y - 40.3) / 2,
                                (field_y + 40.3) / 2, (field_y + 40.3) / 2], color="black")
    ax.plot([field_x, field_x - 16.5, field_x - 16.5, field_x],
            [(field_y - 40.3) / 2, (field_y - 40.3) / 2,
            (field_y + 40.3) / 2, (field_y + 40.3) / 2], color="black")

    # 골키퍼 구역
    ax.plot([0, 5.5, 5.5, 0], [(field_y - 18.32) / 2, (field_y - 18.32) / 2,
                                (field_y + 18.32) / 2, (field_y + 18.32) / 2], color="black")
    ax.plot([field_x, field_x - 5.5, field_x - 5.5, field_x],
            [(field_y - 18.32) / 2, (field_y - 18.32) / 2,
            (field_y + 18.32) / 2, (field_y + 18.32) / 2], color="black")

    # 골대
    ax.plot([0, -2], [(field_y - 7.32) / 2, (field_y - 7.32) / 2], color="black")
    ax.plot([0, -2], [(field_y + 7.32) / 2, (field_y + 7.32) / 2], color="black")
    ax.plot([field_x, field_x + 2], [(field_y - 7.32) / 2, (field_y - 7.32) / 2], color="black")
    ax.plot([field_x, field_x + 2], [(field_y + 7.32) / 2, (field_y + 7.32) / 2], color="black")

    ax.set_xlim(-5, field_x + 5)
    ax.set_ylim(-5, field_y + 5)
    ax.set_aspect("equal", adjustable="box")

    # 히트맵 시각화
    # 히트맵을 축구장 위에 투명하게 덧붙이기
    heatmap_img = ax.imshow(heatmap, cmap='YlGnBu', interpolation='nearest', alpha=0.6, extent=[0, field_x, 0, field_y])

    # 축구장의 크기와 구간을 시각적으로 표시
    ax.set_title(f"{team_name} {type} Heatmap", fontsize=30,fontweight='bold')
    ax.set_xlabel("Width (m)")
    ax.set_ylabel("Height (m)")

    # 범례 추가 (Colorbar)
    cbar = plt.colorbar(heatmap_img, ax=ax)
    cbar.set_label('Pass', rotation=270, labelpad=20, fontsize=15)

    # 범례 구간 구분 (색상에 대한 설명)
    ticks = list(range(1, int(np.max(heatmap)), int(int(np.max(heatmap))/4)))  
    cbar.set_ticks(ticks)


    cbar.set_ticklabels([f'{i}' for i in ticks])

    plt.axis('off')
    plt.show()