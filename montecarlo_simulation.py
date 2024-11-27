import numpy as np
import matplotlib.pyplot as plt

# 시뮬레이션 파라미터 설정
total_population = 51713000  # 한국 전체 인구
years = 46  # 시뮬레이션 할 연도 수 (2025~2070, 46년)
simulations = 100  # 몬테카를로 시뮬레이션 반복 횟수
population_growth = np.linspace(0.14, -1.31, 46).tolist()  # 회귀분석한 인구성장률
go_to_seoul_list = [] #서울로 이동하는 인력

# 지역별 데이터 설정
regions = {
    'Gangwon': {'add': 165, 'gp': [0], 'fellow': [787], 'population': 1525000},
    'Chungbuk': {'add': 211, 'gp': [0], 'fellow': [279], 'population': 1627000},
    'Chungnam': {'add': 338, 'gp': [0], 'fellow': [756], 'population': 3678000},
    'Gyungbuk': {'add': 289, 'gp': [0], 'fellow': [1615], 'population': 4971000},
    'Gyungnam': {'add': 361, 'gp': [0], 'fellow': [1934], 'population': 4390000},
    'Jeonbuk': {'add': 115, 'gp': [0], 'fellow': [416], 'population': 1768000},
    'Jeonnam': {'add': 100, 'gp': [0], 'fellow': [987], 'population': 3231000},
    'Jeju': {'add': 60, 'gp': [0], 'fellow': [323], 'population': 677000},
    'Capital': {'add': 361, 'gp': [0], 'fellow': [9406], 'population': 26190000}
}

# 결과 저장 배열 생성
results = {
    region: {
        'serious_patient_simulation': np.zeros((simulations, years)),
        'gp_simulation': np.zeros((simulations, years)),
        'fellow_simulation': np.zeros((simulations, years)),
        'total_patient_simulation': np.zeros((simulations, years)),
        'unpopular_fellow_simulation': np.zeros((simulations, years)),
    }
    for region in regions
}

# 시뮬레이션 실행
for region, data in regions.items():
    total_cost_list = []

    for sim in range(simulations):
        simulated_years = []
        population = data['population']
        add = data['add']
        fellow = data['fellow'][0]
        gp = data['gp'][0]
        unpopular_fellow = fellow * 0.0775
        go_to_seoul_ratio = 0.32
        total_cost = 0

        for i in range(years):
            # 인구 성장률 적용
            population *= (1 + population_growth[i] / 100)
            # 총 환자수와 중증 환자수 계산
            total_patient = np.random.normal(43981000, 1220000) * (1 + population_growth[i] / 100) * population / total_population / 365
            unpopular_patient = total_patient * 0.311
            serious_patient = unpopular_patient * np.random.normal(0.074, 0.0057)

            # 의사 수 증가 계산
            fellow_ratio = 0.88
            if len(simulated_years) > 10:

                if region != "Capital":
                    go_to_seoul = add*fellow_ratio*go_to_seoul_ratio
                    fellow += add*fellow_ratio*(1 - go_to_seoul_ratio)
                    go_to_seoul_list.append(go_to_seoul)
                    

                else:
                    fellow += add*fellow_ratio + go_to_seoul_list[i]

                total_cost = total_cost + add*fellow_ratio*2.6

                unpopular_fellow = fellow * np.random.normal(0.0775, 0.004)

            if len(simulated_years) > 5:
                gp += add * (1 - fellow_ratio)
                total_cost = total_cost + add * (1 - fellow_ratio) * 8.7


            # 결과 저장
            results[region]['serious_patient_simulation'][sim, i] = serious_patient
            results[region]['gp_simulation'][sim, i] = gp
            results[region]['fellow_simulation'][sim, i] = fellow
            results[region]['unpopular_fellow_simulation'][sim, i] = unpopular_fellow
            results[region]['total_patient_simulation'][sim, i] = total_patient

            simulated_years.append(i + 1)

        total_cost_list.append(total_cost)

    mean = np.mean(total_cost_list)
    print(region," total cost: ",mean )

# subplot 설정 (2행 5열로 배치)
fig, axes = plt.subplots(nrows=3, ncols=3, figsize=(15, 9))  # 2줄 5개로 배치
fig.suptitle('Monte Carlo Simulation Results by Region (Serious Patients(Unpopular Specialty) & Unpopular Specialty)', fontsize=16)

# 각 지역에 대해 그래프 그리기
for idx, (region, data) in enumerate(results.items()):
    row = idx // 3  # 5개의 그래프씩 나누어서 배치
    col = idx % 3
    ax = axes[row, col]
    
    # 평균 계산
    average_serious_patient = np.mean(data['serious_patient_simulation'], axis=0)
    average_unpopular_fellow = np.mean(data['unpopular_fellow_simulation'], axis=0)
    
    # 각 지역에 대한 그래프 그리기
    ax.plot(range(1, years + 1), average_serious_patient, label=f'{region} serious patient/day(unpopular)', color='b')
    ax.plot(range(1, years + 1), average_unpopular_fellow, label=f'{region} unpopular Specialty', color='r')
    
    # 5~95 백분위 범위 채우기 (중증 환자수)
    ax.fill_between(range(1, years + 1),
                    np.percentile(data['serious_patient_simulation'], 5, axis=0),
                    np.percentile(data['serious_patient_simulation'], 95, axis=0),
                    color='b', alpha=0.2)
    
    # 5~95 백분위 범위 채우기 (비인기과 의사 수)
    ax.fill_between(range(1, years + 1),
                    np.percentile(data['unpopular_fellow_simulation'], 5, axis=0),
                    np.percentile(data['unpopular_fellow_simulation'], 95, axis=0),
                    color='r', alpha=0.2)
    
    ax.set_title(f'{region}')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number')
    ax.grid(True)
    ax.legend()


plt.tight_layout(rect=[0, 0, 1, 0.95])  # 제목과 그래프 레이아웃 조정
plt.show()

