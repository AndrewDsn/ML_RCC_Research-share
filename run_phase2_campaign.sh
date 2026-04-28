#!/bin/bash
# Phase 2 Full Campaign Execution Script
# Execute verified PEER NGA earthquake records campaign
# Time: 8-12 hours (8-core) | 1-3 hours (64-core cloud)

set -e  # Exit on error

echo ""
echo "=========================================================================="
echo "PHASE 2: FULL VERIFIED RECORDS CAMPAIGN"
echo "=========================================================================="
echo ""
echo "This script executes the complete Phase 2 workflow:"
echo "  1. Generate 80 Phase 1 parametric RC models (30-60 sec)"
echo "  2. Run pilot test with 2 GMs/zone (2-5 min)"
echo "  3. Execute full campaign with 8 GMs/zone (8-12 hours)"
echo ""
echo "Total Time: 8-12 hours (8-core) | 1-3 hours (64-core cloud)"
echo "Output: data/processed/ida_results_verified.csv (~51,200 records)"
echo ""
echo "=========================================================================="
echo ""

# Navigate to project directory
cd "$(dirname "$0")/project"

# Verify directories exist
mkdir -p models/openseespy
mkdir -p data/processed
mkdir -p results/logs

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Phase 2 campaign..."
echo ""

# Execute the master script
python run_phase2_full.py

echo ""
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Phase 2 campaign complete!"
echo ""
echo "Output file: project/data/processed/ida_results_verified.csv"
echo ""
echo "Next Steps:"
echo "  1. Verify output file exists and has 40,000+ records"
echo "  2. Begin Phase 3: ML model training"
echo ""
echo "=========================================================================="
