import hamarr as ham
import subprocess as spr
import numpy as np


class mjol_args:
    # make_plot args, populate with defaults
    def __init__(self, file):
        self.pview = []
        self.file = [file]
        self.simulation_ID = ['auto']
        self.initial_file = [10]
        self.last_file = ['init']
        self.horizontal_lev = [2.5e2]
        self.vertical_top = ['default']
        self.split_layer = ['no_split']
        self.coordinate_sys = ['icoh']
        self.lmax_adjust = [0]
        self.slice = [0, 360]
        self.maketable = False
        self.no_pressure_log = False
        self.latlonswap = False
        self.vcoord = ['pressure']
        self.pgrid_ref = ['auto']
        self.clevels = [40]


def make_plot(args):
    pview = args.pview

    maketable = args.maketable
    plog = True
    if args.no_pressure_log:
        plog = False

    valid = ['uver', 'ulonver', 'vver', 'wver', 'wlonver', 'wprof', 'Tver', 'Tlonver', 'Tulev', 'PTver', 'PTlonver', 'ulev', 'PVver', 'PVlev',
             'TP', 'RVlev', 'cons', 'stream', 'pause', 'tracer', 'PTP', 'regrid', 'KE',
             'SR', 'uprof', 'cfl', 'bvprof', 'fluxprof', 'Tsurf', 'insol', 'massf',
             'futprof', 'fdtprof', 'fnetprof', 'mustar', 'fuptot', 'fdowntot', 'fnet', 'qheat'  # alf stuff
             ]

    rg_needed = ['Tver', 'Tlonver', 'uver', 'ulonver', 'vver', 'wver', 'wlonver', 'Tulev', 'PTver', 'PTlonver', 'ulev', 'PVver', 'PVlev',
                 'RVlev', 'stream', 'tracer', 'Tsurf', 'insol', 'massf',
                 'mustar', 'fuptot', 'fdowntot', 'fnet', 'qheat']  # these types need regrid

    openrg = 0
    if 'all' in pview:
        pview = valid
        openrg = 1
    else:
        for p in pview:
            if openrg == 0 and p in rg_needed:
                openrg = 1
            if p not in valid:
                raise ValueError('%s not a valid plot option. Valid options are ' % p + ', '.join(valid))

    ntsi = args.initial_file[0]  # initial file id number

    if args.last_file[0] == 'init':
        nts = ntsi
    else:
        nts = args.last_file[0]     # last file id number

    if ntsi > nts:
        nts = ntsi

    resultsf = args.file[0]
    if args.simulation_ID[0] == 'auto':
        outname = spr.check_output('ls ' + resultsf + '/esp_output_*_0.h5', shell=True)
        file0 = outname.decode().split(sep='/')[-1]
        simulation_ID = file0.split(sep='_')[2]
    else:
        simulation_ID = args.simulation_ID[0]

    if args.vcoord[0] == 'pressure':
        use_p = True
    elif args.vcoord[0] == 'height':
        use_p = False
        plog = False  # enforce this on height grid
    else:
        raise ValueError('%s not a valid vcoord. Valid options are "pressure" or "height"' % args.vcoord[0])

    # regrid function is a special case and interrupts the other stuff
    if 'regrid' in pview:
        ham.regrid(resultsf, simulation_ID, ntsi, nts, pressure_vert=use_p, pgrid_ref=args.pgrid_ref[0])
        exit()

    outall = ham.GetOutput(resultsf, simulation_ID, ntsi, nts, openrg=openrg,
                           pressure_vert=use_p, pgrid_ref=args.pgrid_ref[0])

    ##########
    # Planet #
    ##########

    input = outall.input

    ########
    # Grid #
    ########

    grid = outall.grid

    ###############
    # Diagnostics #
    ###############

    output = outall.output

    ##################
    # Regridded data #
    ##################
    if openrg == 1:
        rg = outall.rg

    # quick and dirty break point, if you just want to look at the output data
    # does not load regridded data!
    if 'pause' in pview:
        import pdb
        pdb.set_trace()

    #########
    # Plots #
    #########

    plots_created = []
    # --- Vertical plot types-------------------------------
    if 'uver' in pview:
        z = {'value': rg.U, 'label': r'Velocity (m s$^{-1}$)', 'name': 'u',
             'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged zonal winds (latitude vs pressure)
        # ham.u(input,grid,output,rg,sigmaref,slice=args.slice[0])
        pfile = ham.vertical_lat(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=1000, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'ulonver' in pview:
        z = {'value': rg.U, 'label': r'Velocity (m s$^{-1}$)', 'name': 'u',
             'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged zonal winds (latitude vs pressure)
        # ham.u(input,grid,output,rg,sigmaref,slice=args.slice[0])
        pfile = ham.vertical_lon(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=1000, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'vver' in pview:
        z = {'value': rg.V, 'label': r'Velocity (m s$^{-1}$)', 'name': 'v',
             'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged zonal winds (latitude vs pressure)
        # ham.u(input,grid,output,rg,sigmaref,slice=args.slice[0])
        pfile = ham.vertical_lat(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'wver' in pview:
        z = {'value': rg.W, 'label': r'Velocity (m s$^{-1}$)', 'name': 'w',
             'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged vertical winds (latitude vs pressure)
        # ham.w_ver(input,grid,output,rg,sigmaref)
        pfile = ham.vertical_lat(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=1, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'wlonver' in pview:
        z = {'value': rg.W, 'label': r'Velocity (m s$^{-1}$)', 'name': 'w',
             'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged zonal winds (latitude vs pressure)
        # ham.u(input,grid,output,rg,sigmaref,slice=args.slice[0])
        pfile = ham.vertical_lon(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=5, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'Tver' in pview:
        z = {'value': rg.Temperature, 'label': r'Temperature (K)', 'name': 'temperature',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged temperature (latitude vs pressure)
        # ham.temperature(input,grid,output,rg,sigmaref)
        pfile = ham.vertical_lat(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=[0], clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'Tlonver' in pview:
        z = {'value': rg.Temperature, 'label': r'Temperature (K)', 'name': 'temperature',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged temperature (latitude vs pressure)
        # ham.temperature(input,grid,output,rg,sigmaref)
        pfile = ham.vertical_lon(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=[0], clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'PTver' in pview:
        kappa_ad = input.Rd / input.Cp  # adiabatic coefficient
        pt = rg.Temperature * (rg.Pressure / input.P_Ref)**(-kappa_ad)
        z = {'value': pt, 'label': r'Potential Temperature (K)', 'name': 'potential_temp',
             'cmap': 'plasma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged potential temperature (latitude vs pressure)
        pfile = ham.vertical_lat(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=5000, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'PTlonver' in pview:
        kappa_ad = input.Rd / input.Cp  # adiabatic coefficient
        pt = rg.Temperature * (rg.Pressure / input.P_Ref)**(-kappa_ad)
        z = {'value': pt, 'label': r'Potential Temperature (K)', 'name': 'potential_temp',
             'cmap': 'plasma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        # Averaged potential temperature (latitude vs pressure)
        pfile = ham.vertical_lon(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=5000, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'PVver' in pview:
        # sigmaref = np.arange(1,0,)
        z = {'value': rg.PV, 'label': r'Potential Vorticity (K m$^2$ kg$^{-1}$ s$^{-1}$)',
             'name': 'pot_vort', 'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
        sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
        pfile = ham.vertical_lat(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, clevs=args.clevels)
        # ham.potential_vort_vert(input,grid,output,sigmaref)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'stream' in pview:  # RD: needs some work! to adapt to height coordinate
        # strm = ham.calc_moc_streamf(input,grid,output)
        # strm = rg.streamf
        # z = {'value':strm, 'label':r'Eulerian streamfunction (kg s$^{-1}$)', 'name':'streamf2',
        #      'cmap':'viridis', 'lat':rg.lat, 'lon':rg.lon}
        if use_p:
            sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
            # ham.vertical_lat(input,grid,output,rg,sigmaref,z,slice=args.slice,csp=[0])
            pfile = ham.streamf_moc_plot(input, grid, output, rg, sigmaref, mt=maketable, plog=plog, clevs=args.clevels)
            if pfile:
                print('Created file: ' + pfile)
                plots_created.append(pfile)
        else:
            raise ValueError("'stream' plot type requires -vc pressure")
            # no reason to keep this way, just need to fix to use height
    if 'massf' in pview:
        if use_p == False:
            # mass flow rate (zonal average)
            massfdl = (input.A + rg.Altitude[None, None, :, :]) * np.cos(rg.lat[:, None, None, :] * np.pi / 180) / (2 * np.pi) * rg.Rho * rg.V
            z = {'value': massfdl, 'label': r'Mass flow', 'name': 'massf',
                 'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'plog': plog}
            sigmaref = ham.Get_Prange(input, grid, rg, args, xtype='lat', use_p=use_p)
            pfile = ham.vertical_lat(input, grid, output, rg, sigmaref, z, slice=args.slice, use_p=use_p, csp=[0], clevs=args.clevels)
            if pfile:
                print('Created file: ' + pfile)
                plots_created.append(pfile)
        else:
            raise ValueError("'massf' plot type requires -vc height")

    # --- Horizontal plot types-------------------------------
    # need to be updated for height coordinates
    if 'Tulev' in pview:
        # Averaged temperature and wind field (longitude vs latitude)
        # PR_LV - Pressure level (Pa)
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.Temperature, 'label': r'Temperature (K)', 'name': 'temperature-uv',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'ulev' in pview:
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.U, 'label': r'Zonal Velocity (m s$^{-1}$)', 'name': 'u',
             'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
        z = {'value': rg.V, 'label': r'Meridional Velocity (m s$^{-1}$)', 'name': 'v',
             'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'PVlev' in pview:
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.PV, 'label': r'Potential Vorticity (K m$^2$ kg$^{-1}$ s$^{-1}$)',
             'name': 'pot_vort', 'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
        # ham.potential_vort_lev(input,grid,output,PR_LV)
    if 'RVlev' in pview:
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.RV, 'label': r'Relative Vorticity (s$^{-1}$)',
             'name': 'rela_vort', 'cmap': 'viridis', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
        # ham.rela_vort_lev(input,grid,output,PR_LV)
    if 'tracer' in pview:
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': np.log10(rg.ch4), 'label': r'Log(mixing ratio)',
             'name': 'chem-ch4-uv1', 'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
        z = {'value': np.log10(rg.co), 'label': r'Log(mixing ratio)',
             'name': 'chem-co-uv1', 'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
        z = {'value': np.log10(rg.h2o), 'label': r'Log(mixing ratio)',
             'name': 'chem-h2o-uv1', 'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
        z = {'value': np.log10(rg.co2), 'label': r'Log(mixing ratio)',
             'name': 'chem-co2-uv1', 'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
        z = {'value': np.log10(rg.nh3), 'label': r'Log(mixing ratio)',
             'name': 'chem-nh3-uv1', 'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'insol' in pview:
        PR_LV = np.max(output.Pressure)  # not important here
        z = {'value': rg.insol, 'label': r'Insolation (W m$^{-2}$)', 'name': 'insol',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'Tsurf' in pview:
        if not hasattr(rg, "Tsurface"):
            raise ValueError("'Tsurface' not available in regrid file")
        PR_LV = np.max(output.Pressure)  # not important here
        z = {'value': rg.Tsurface, 'label': r'Surface Temperature (K)', 'name': 'Tsurf',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)

    if 'fuptot' in pview:
        # Averaged temperature and wind field (longitude vs latitude)
        # PR_LV - Pressure level (Pa)
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.f_up_tot, 'label': r'Total upward flux (W m^-2)', 'name': 'fuptot',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'fdowntot' in pview:
        # Averaged temperature and wind field (longitude vs latitude)
        # PR_LV - Pressure level (Pa)
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.f_down_tot, 'label': r'Total downward flux (W m^-2)', 'name': 'fdowntot',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'fnet' in pview:
        # Averaged temperature and wind field (longitude vs latitude)
        # PR_LV - Pressure level (Pa)
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.f_net, 'label': r'Total net flux (W m^-2)', 'name': 'fnet',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'qheat' in pview:
        # Averaged temperature and wind field (longitude vs latitude)
        # PR_LV - Pressure level (Pa)
        if use_p:
            PR_LV = np.float(args.horizontal_lev[0]) * 100
        else:
            PR_LV = np.float(args.horizontal_lev[0]) * 1000
        z = {'value': rg.q_heat, 'label': r'Q Heat (W m^-3)', 'name': 'qheat',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    if 'mustar' in pview:
        PR_LV = np.max(output.Pressure)  # not important here
        z = {'value': rg.mustar, 'label': r'mu_star ', 'name': 'mustar',
             'cmap': 'magma', 'lat': rg.lat, 'lon': rg.lon, 'mt': maketable, 'llswap': args.latlonswap}
        pfile = ham.horizontal_lev(input, grid, output, rg, PR_LV, z, wind_vectors=True, use_p=use_p, clevs=args.clevels)
        if pfile:
            print('Created file: ' + pfile)
            plots_created.append(pfile)
    # --- Pressure profile types-------------------------------
    if 'TP' in pview:
        z = {'value': output.Pressure / output.Rd / output.Rho, 'label': 'Temperature (K)', 'name': 'T'}
        # ham.TPprof(input,grid,output,sigmaref,1902)
        ham.profile(input, grid, output, z)
    if 'PTP' in pview:
        # kappa_ad = input.Rd/input.Cp  # adiabatic coefficient
        kappa_ad = output.Rd / output.Cp
        T = output.Pressure / input.Rd / output.Rho
        pt = T * (output.Pressure / input.P_Ref)**(-kappa_ad)
        z = {'value': pt, 'label': 'Potential Temperature (K)', 'name': 'PT'}
        ham.profile(input, grid, output, z)
    if 'wprof' in pview:  # RD: needs some work!
        z = {'value': output.Wh[:, 1:, :] / output.Rho, 'label': r'Vertical velocity (m s$^{-1}$)', 'name': 'W'}
        ham.profile(input, grid, output, z, stride=20)
        # Averaged vertical winds (latitude vs pressure)
        # ham.w_prof(input,grid,output)
    if 'uprof' in pview:  # RD: needs some work!
        u = (-output.Mh[0] * np.sin(grid.lon[:, None, None]) + output.Mh[1] * np.cos(grid.lon[:, None, None])) / output.Rho
        z = {'value': u, 'label': r'Zonal velocity (m s$^{-1}$)', 'name': 'U'}
        ham.profile(input, grid, output, z, stride=20)
    if 'cfl' in pview:
        dt = output.time[0] / output.nstep[0] * 86400
        dx = np.sqrt(np.min(grid.areasT))
        cs = np.sqrt(input.Cp / (input.Cp - input.Rd) * output.Pressure / output.Rho)
        z = {'value': cs * dt / dx, 'label': 'CFL number for (horizontal) acoustic waves', 'name': 'CFL'}
        ham.profile(input, grid, output, z, stride=20)
    if 'bvprof' in pview:
        kappa_ad = input.Rd / input.Cp  # adiabatic coefficient
        T = output.Pressure / input.Rd / output.Rho
        pt = T * (output.Pressure / input.P_Ref)**(-kappa_ad)
        dptdr = np.gradient(pt, grid.Altitude, axis=1)
        N = np.sqrt(input.Gravit / pt * dptdr)
        z = {'value': N, 'label': r'$N$ (s$^{-1}$)', 'name': 'BVprof'}
        ham.profile(input, grid, output, z, stride=20)
    if 'fluxprof' in pview:
        total_f = output.fnet_up - output.fnet_dn
        fup = total_f[:, :-1, :] + (total_f[:, 1:, :] - total_f[:, :-1, :]) *\
            (grid.Altitude[None, :, None] - grid.Altitudeh[None, :-1, None]) /\
            (grid.Altitudeh[None, 1:, None] - grid.Altitudeh[None, :-1, None])
        z = {'value': fup, 'label': r'Total flux (W m$^{-2}$)', 'name': 'ftot'}
        ham.profile(input, grid, output, z, stride=20)
    if 'futprof' in pview:
        fup = output.f_up_tot[:, :-1, :]
        z = {'value': fup, 'label': r'Total Upward flux (W m$^{-2}$)', 'name': 'fuptot'}
        ham.profile(input, grid, output, z, stride=20)
    if 'fdtprof' in pview:
        fdn = output.f_down_tot[:, :-1, :]
        z = {'value': fdn, 'label': r'Total Downward flux (W m$^{-2}$)', 'name': 'fdowntot'}
        ham.profile(input, grid, output, z, stride=20)
    if 'fnetprof' in pview:
        fdn = output.f_net[:, :-1, :]
        z = {'value': fdn, 'label': r'Total Net flux (W m$^{-2}$)', 'name': 'fnetprof'}
        ham.profile(input, grid, output, z, stride=20)

    # --- Global diagnostics -----------------------------------
    if 'cons' in pview:  # RD: needs some work!
        if args.split_layer[0] == 'no_split':
            split = False
        else:
            split = np.float(args.split_layer[0]) * 100
        ham.conservation(input, grid, output, split)
    if 'KE' in pview:  # RD: needs some work!
        PR_LV = np.float(args.horizontal_lev[0]) * 100  # not actually used here
        ham.KE_spect(input, grid, output, PR_LV, coord=args.coordinate_sys[0], lmax_adjust=args.lmax_adjust[0])
    if 'SR' in pview:
        ham.SRindex(input, grid, output)
    if 'RTbalance' in pview:
        ham.RTbalance(input, grid, output)

    return plots_created
