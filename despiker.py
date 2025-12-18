import yaml

import matplotlib.pyplot as plt



def despiked(values: list, arguments: list=[], window: int=5, multipass: int=1) -> (list, list):
    """
    Dataseries despiker
    
    Arguments:

        values    : list[int, float] of values (Y's)
        arguments : list[int, float] of arguments (X'es) - automatically generated when not provided
                    both lists should be an equal length otherwise the longer list will be truncated 

        window    : int - length of data window in which spikes will be searched
                    (smaller window = more precise despiking) 

        multipass : int - number of despiking passes

    Return:
        tuple (arguments: list, values: list)
    """

    assert window >= 3 and window % 2, "window size should be an odd number >= than 3"
    ndata = [[t, v] for t, v in zip(arguments if arguments else range(len(values)), values)]
    for mpass in range(multipass):
        spikes = []
        for i in range(len(ndata) - (window - 1)):
            data_window = ndata[i: i + window]
            
            # find min and max data point in the data_window
            vmin, vmax = min(data_window, key=lambda x: x[1]), max(data_window, key=lambda x: x[1])

            # calculate height of the data_window
            # if vmin or vmax is inside the data_window (excluding 1st and last data_pioint)
            h = vmax[1] - vmin[1] if vmax in data_window[1:-1] or vmin in data_window[1:-1] else 0

            # calculate length of the window (it matters if distribution of the x'es is non linear)
            b = data_window[-1][0] - data_window[0][0]

            # calculate data spike as a ratio of max height and length of the data_window
            spike = h / b
            spikes.append((i, spike, data_window))

        if spikes:
            # calculate average spike hight
            avg_spike = sum([v for _, v, _ in spikes]) / len(spikes)
            for spike_index, spike_height, spike_data in spikes:
                if spike_height > avg_spike:
                    # if spike_height is greater than avg_spike
                    # recalculate values of spike_data as an average of 2 neighbouring data_points
                    # and replace them in the input data
                    for i in range(1, len(spike_data) - 1):
                        ndi = spike_index + i
                        ndata[ndi][-1] = (ndata[ndi - 1][-1] + ndata[ndi + 1][-1]) / 2

    return ([t for t, _ in ndata], [v for _, v in ndata])


if __name__ == "__main__":
    with open("./test_data.json") as df:
        data = yaml.safe_load(df)[:1440]

    arguments, values = [t for t, _ in data], [v for _, v in data]

    fig, (plot_mp, plot_w) = plt.subplots(2, 1, sharex=True, sharey=True)
    fig.tight_layout()

    plot_mp.plot(arguments, values, label="Original data")
    for p in [1, 3, 5, 7]:
        nx, ny = despiked(values, arguments, window=5, multipass=p)
        plot_mp.plot(nx, ny, label=f"Despiked data: multipass = {p}")

    plot_mp.grid()
    plot_mp.legend()


    plot_w.plot(arguments, values, label="Original data")
    for w in [3, 9, 15, 21]:
        nx, ny = despiked(values, arguments, window=w, multipass=1)
        plot_w.plot(nx, ny, label=f"Despiked data: window = {w}")

    plot_w.grid()
    plot_w.legend()

    plt.show()
