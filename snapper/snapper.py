from argparse import ArgumentParser
from webbrowser import get
from snapper.src.motif_extraction import get_seqs, extract_motifs, merge_motifs, collapse_motifs
from snapper.src.plotting import plot_motif
from snapper.src.data_processing import parse_data
from snapper.src.statistics import get_difsignals, get_statistics, save_results
from snapper.src.statistics import SAMPLESIZE, MINSAMPLESIZE, LOG10_PVAL_TRH, EFFSIZE_TRH
import os
import sys




def main():



    parser = ArgumentParser()

    parser.add_argument('-sample_fast5dir', type=str, help='sample multi fast5 dir')
    parser.add_argument('-control_fast5dir', type=str, help='control multi fast54 dir')
    parser.add_argument('-reference', type=str, help='reference fasta')
    parser.add_argument('-ks_t', type=int, default=50, help='-log ks_test p-value (default 50)')
    parser.add_argument('-eff_size', type=float, default=0.25, help='Cohen d-effect size (default 0.25)')
    parser.add_argument('-outdir', type=str, default='default', help='output directory name')
    parser.add_argument('-n_batches', type=int, default=100, help='number of parsed fast5 batches')
    
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    args = parser.parse_args()


    print('\nSample data collecting...')

    sample_shifts, sample_reverse_shifts, sample_motifs, sample_reverse_motifs = parse_data(
        args.sample_fast5dir, 
        args.reference, 
        target_chr='all', 
        n_batches=args.n_batches, 
    )

    print('dsflsdkfjsldfkjdslfjk')


    print('\nControl data collecting...')
    control_shifts, control_reverse_shifts, control_motifs, control_reverse_motifs = parse_data(
        args.control_fast5dir, 
        args.reference, 
        target_chr='all', 
        n_batches=args.n_batches, 
    )


    print('\nForward strand singnals processing...')
    motifs_lines, ks_stat_lines, effsize_lines = get_statistics(
        sample_motifs, 
        control_motifs, 
        maxsamplesize=SAMPLESIZE,
        minsamplesize=MINSAMPLESIZE,
    )


    print('\Reverse strand singnals processing...')
    reverse_motifs_lines, reverse_ks_stat_lines, reverse_effsize_lines = get_statistics(
        sample_reverse_motifs, 
        control_reverse_motifs, 
        maxsamplesize=SAMPLESIZE,
        minsamplesize=MINSAMPLESIZE,
    )



    if args.outdir == 'default':
        import datetime
        
        sp = str(datetime.datetime.now()
            ).replace(' ', '_').replace(':', '').replace('-', '_').split('.')[0]
        outdir = 'Results_' + sp

    else:
        outdir  = args.outdir

    try:
        os.mkdir(outdir)
    except:
        raise FileExistsError('The specified output dir already exists!')
        


    # MOTIFS EXTRACTION

    for contig in motifs_lines:

        print('Processing forward motifs {}...'.format(contig))
            

        contig_passed_motifs = get_difsignals(
            motifs_lines[contig], 
            ks_stat_lines[contig], 
            effsize_lines[contig],
            log10_pval_thr = args.ks_t,
            effsize_thr = args.eff_size
        )

        plotdir = outdir + '/plots_forward_{}'.format(contig) 
        os.mkdir(plotdir)

        motifs = collapse_motifs(extract_motifs(contig_passed_motifs))

        for motif in motifs:
            plot_motif(sample_motifs[contig], control_motifs[contig], motif, plotdir)



        save_results(contig_passed_motifs, outdir + '/passed_motifs_forward_{}.fasta'.format(contig))
        save_results(motifs, outdir + '/final_motifs_forward_{}.fasta'.format(contig))


    for contig in reverse_motifs_lines:

        print('Processing reversed motifs {}...'.format(contig))
            

        contig_passed_motifs = get_difsignals(
            reverse_motifs_lines[contig], 
            reverse_ks_stat_lines[contig], 
            reverse_effsize_lines[contig],
            log10_pval_thr = args.ks_t,
            effsize_thr = args.eff_size
        )

        plotdir = outdir + '/plots_reverse_{}'.format(contig) 
        os.mkdir(plotdir)

        motifs = collapse_motifs(extract_motifs(contig_passed_motifs))

        for motif in motifs:
            plot_motif(sample_motifs[contig], control_motifs[contig], motif, plotdir)



        save_results(contig_passed_motifs, outdir + '/passed_motifs_reverse_{}.fasta'.format(contig))
        save_results(motifs, outdir + '/final_motifs_reverse_{}.fasta'.format(contig))

    
    # MODIFIED POSITIONS EXTRACTION



    for contig in sample_shifts:

        pass
        





    print('Done!')


if __name__ == '__main__':
    main()