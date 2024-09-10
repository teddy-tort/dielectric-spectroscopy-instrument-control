import slowplot
import os
import data_files

if __name__ == "__main__":
    import sys; sys.path.append('..')
    import GPIB.get as get

    filepath = os.path.join(get.google_drive(), 'Dielectric_data', 'Teddy')
    filenames = data_files.file_name(6, 15, 2016)
    plotters = []
    for filename in filenames:
        plotters.append(slowplot.Plotter(filepath, filename))
    for plotter in plotters:
        plotter.plot_loss_v_temp()
        plotter.plot_loss_v_time()
        plotter.plot_temp_v_time()
        plotter.plot_cap_v_temp()
        plotter.plot_cap_v_time()
        plotter.show()
