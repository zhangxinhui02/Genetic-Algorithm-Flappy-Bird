import random
import subprocess
import json
import copy
import matplotlib.pyplot as plt

import config


def plot(generation, score):
    plt.ion()
    plt.plot(generation, score)
    plt.title('Fitness Change Curve')
    plt.xlabel('Generation')
    plt.ylabel('Fitness(Best Score)')
    plt.show()
    plt.pause(0.1)
    plt.ioff()


def run():
    birds_generations = {}
    last_times = [[random.random() * config.time_range_sec] for _ in range(config.birds_count_each_generation)]
    last_scores = [0 for _ in range(config.birds_count_each_generation)]
    best_times = [random.random() * config.time_range_sec]
    best_score = 0
    outputs = []

    plot_generation = [0]
    plot_score = [0]
    plot(plot_generation, plot_score)
    print('Please move the plot window to the appropriate position within 5 seconds.')
    plt.pause(5)

    for generation in range(1, config.simulation_generations + 1):
        birds_generations[generation] = {
            'best_score': None,
            'best_times': None,
            'times': []
        }
        birds_pool = []
        for times, score in zip(last_times, last_scores):
            for _ in range(int((score + 1) ** config.better_k)):
                birds_pool.append(copy.copy(times))
        birds_pool = random.sample(birds_pool, config.birds_count_each_generation - 1)

        # 复制最优个体
        birds_pool.append(copy.copy(best_times))
        # 染色体交叉
        # fork_index = []
        # for idx in range(birds_count_each_generation - 1):
        #     if len(birds_pool[idx]) < len(birds_pool[idx + 1]):
        #         fork_index.append(random.randint(0, len(birds_pool[idx]) - 1))
        #     else:
        #         fork_index.append(random.randint(0, len(birds_pool[idx+1]) - 1))
        # for idx in range(birds_count_each_generation - 1):
        #     birds_pool[idx][fork_index[idx]] = birds_pool[idx+1][fork_index[idx]]
        # 基因突变
        for idx in range(config.birds_count_each_generation - 1):
            if random.random() < config.change_rate:
                birds_pool[idx][-1] = random.random() * config.time_range_sec
            if random.random() < config.change_rate:
                try:
                    assert birds_pool[idx][-2]
                    birds_pool[idx][-2] = random.random() * config.time_range_sec
                except IndexError:
                    pass
        for idx in range(config.birds_count_each_generation):
            input_args = [str(time) for time in birds_pool[idx]]
            input_args = ['python', 'runner.py'] + input_args
            output = subprocess.Popen(input_args, stdout=subprocess.PIPE, shell=True)
            outputs.append(output)

        print('=================================')
        print(f'Generation {generation} started.')
        print('=================================')
        cache_best_times = best_times
        cache_best_scores = best_score
        best_times = []
        last_scores = []
        last_times = []
        bird_count = 1
        best_score = 0
        while True:
            rm_list = []
            for idx, output in enumerate(outputs):
                if output.poll() is not None:
                    output.terminate()
                    # time.sleep(0.1)
                    msg = output.stdout.readlines()[-1].decode('utf-8').strip()
                    data = json.loads(msg)
                    rm_list.append(output)
                    last_scores.append(data[0])
                    last_times.append(data[1])
                    birds_generations[generation]['times'].append(data[1])
                    if data[0] > best_score:
                        best_score = data[0]
                        best_times = data[1]
                    print('=================================')
                    print(f'Bird {bird_count} game over.\n\tScore: {data[0]}')
                    print('=================================')
                    bird_count += 1
            for rm_i in rm_list:
                outputs.remove(rm_i)
            if len(best_times) == 0:
                best_score = cache_best_scores
                best_times = cache_best_times
            if len(outputs) == 0:
                print('=================================')
                print(f'Generation {generation} finished.\n\tBest score: {best_score}')
                print('=================================')
                birds_generations[generation]['best_times'] = best_times
                birds_generations[generation]['best_score'] = best_score
                plot_generation.append(generation)
                plot_score.append(best_score)
                plot(plot_generation, plot_score)

                break
    plt.savefig('result/fitness.jpg')
    with open('result/outputs.json', 'w', encoding='utf-8') as f:
        json.dump(birds_generations, f, indent=4, ensure_ascii=False)
