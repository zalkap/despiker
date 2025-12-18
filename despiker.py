import yaml

import matplotlib.pyplot as plt



def despiked(
        values: list,
        arguments: list=[],
        window: int=5,
        multipass: int=1,
        method: str="mean") -> (list, list):
    """
    Dataseries despiker
    
    Arguments:

        values    : list[int, float] of values (Y's)
        arguments : list[int, float] of arguments (X'es) - automatically generated when not provided
                    both lists should be an equal length otherwise the longer list will be truncated 

        window    : int - length of data window in which spikes will be searched
                    (smaller window = more precise despiking) 

        multipass : int - number of despiking passes
        
        method :    str - <"median", "mean"> method of calculating threshold value of a spike

    Return:
        tuple (arguments: list, values: list)
    """

    assert window >= 3 and window % 2, "window size should be an odd number >= than 3"
    assert method in ["median", "mean"], "the method should be either 'median' or 'avg'"
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
            # calculate spike_condition
            match method:
                case "median":
                    _, spike_condition, _ = sorted(spikes, key=lambda e: e[1])[(len(spikes) // 2) + 1]
                case "mean":
                    spike_condition = sum([v for _, v, _ in spikes]) / len(spikes)

            for spike_index, spike_height, spike_data in spikes:
                if spike_height > spike_condition:
                    # if spike_height is greater than avg_spike
                    # recalculate values of spike_data as an average of 2 neighbouring data_points
                    # and replace them in the input data
                    for i in range(1, len(spike_data) - 1):
                        ndi = spike_index + i
                        ndata[ndi][-1] = (ndata[ndi - 1][-1] + ndata[ndi + 1][-1]) / 2

    return ([t for t, _ in ndata], [v for _, v in ndata])


if __name__ == "__main__":
    with open("./test_data.json") as df:
        data = yaml.safe_load(df)[:]

    arguments, values = [t for t, _ in data], [v for _, v in data]

    fig, (plot_multipass, plot_window, plot_method) = plt.subplots(3, 1, sharex=True, sharey=True)
    fig.tight_layout()

    plot_multipass.plot(arguments, values, label="Original data")
    w = 5
    for p in [1, 3, 5, 7]:
        nx, ny = despiked(values, arguments, window=w, multipass=p)
        plot_multipass.plot(nx, ny, label=f"Despiked data: window = {w}, multipass = {p}")
    plot_multipass.grid()
    plot_multipass.legend()

    plot_window.plot(arguments, values, label="Original data")
    p = 1
    for w in [3, 9, 15, 21]:
        nx, ny = despiked(values, arguments, window=w, multipass=p)
        plot_window.plot(nx, ny, label=f"Despiked data: window = {w}, multipass = {p}")
    plot_window.grid()
    plot_window.legend()
    
    plot_method.plot(arguments, values, label="Original data")
    w, p = 9, 3
    nx, ny = despiked(values, arguments, window=9, multipass=3, method="mean")
    plot_method.plot(nx, ny, label=f"Mean: window = {w}, multipass = {p}")
    nx, ny = despiked(values, arguments, window=9, multipass=3, method="median")
    plot_method.plot(nx, ny, label=f"Median: window = {w}, multipass = {p}")
    plot_method.grid()
    plot_method.legend()

    plt.show()
