python main.py -n AI-basketball-analysis > ./detection_result/AI-basketball-analysis.log
echo "Testing project(s) 1/10..."
python main.py -n CFL > ./detection_result/CFL.log
echo "Testing project(s) 2/10..."
python main.py -n gcn > ./detection_result/gcn.log
echo "Testing project(s) 3/10..."
python main.py -n noise2noise > ./detection_result/noise2noise.log
echo "Testing project(s) 4/10..."
python main.py -n polyrnn-pp > ./detection_result/polyrnn-pp.log
echo "Testing project(s) 5/10..."
python main.py -n QANet > ./detection_result/QANet.log
echo "Testing project(s) 6/10..."
python main.py -n Rewrite > ./detection_result/Rewrite.log
echo "Testing project(s) 7/10..."
python main.py -n StyleGAN-Tensorflow > ./detection_result/StyleGAN-Tensorflow.log
echo "Testing project(s) 8/10..."
python main.py -n tensorflow-deeplab-v3-plus > ./detection_result/tensorflow-deeplab-v3-plus.log
echo "Testing project(s) 9/10..."
python main.py -n text-classification-cnn-rnn > ./detection_result/text-classification-cnn-rnn.log
echo "Finished Testing on 10 projects!"
