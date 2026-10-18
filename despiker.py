__author__ = "Marcin Zalewski"
__version__ = 1.0


def despiked(
        values: list,
        arguments: list = [],
        window: int = 5,
        multipass: int = 1,
        method: str = "mean") -> (list, list):

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
    help(despiked)
