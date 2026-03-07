%% 1. 加载数据
%data_file = 'J:\data_edited2\457fed 8fast.mat'; 

% 自动获取变量名（以防不叫 data）
%vars = fieldnames(raw_data);
%data = raw_data.(vars{1}); 

%% 2. 设置截取参数 (根据需要修改这里)
% 如果你想看最开始，设置 start_point = 1
% 如果想看中间，可以参考你之前的图（比如 500,000 左右）


% start_point = 200000;  
% num_points = 100000;    % 截取一万个点，如果还是太挤，就改成 5000
% 
% end_point = start_point + num_points;
% 
% % 确保索引不超出数据范围
% [total_samples, num_channels] = size(data);
% end_point = min(end_point, total_samples);
% range = start_point : end_point;
% 
% %% 3. 绘图
% fig = figure('Color', 'w', 'Name', '局部波形细节观察');
% 
% for i = 1:num_channels
%     ax(i) = subplot(num_channels, 1, i); % 记录每个子图的句柄，用于后续联动
% 
%     % 截取数据并去趋势（去除基线漂移，使波形居中）
%     segment = data(range, i);
%     signal_clean = detrend(segment);
% 
%     % 绘图
%     plot(range, signal_clean, 'LineWidth', 1);
% 
%     % 视觉优化
%     ylabel(['Ch ', num2str(i)]);
%     grid on;
%     axis tight; 
% 
%     % 只有最下方的图显示 X 轴编号
%     if i < num_channels
%         set(gca, 'XTickLabel', []); 
%     end
% end
% 
% xlabel('Sample Points');
% sgtitle(['cut：from ', num2str(start_point), ' to ', num2str(end_point), ' point']);
% 
% %% 4. 开启联动缩放 (关键步骤)
% % 这样你用鼠标放大任何一个子图的横坐标，其他 5 个通道会同步移动
% linkaxes(ax, 'x');
% 
% fprintf('finish script.use zoom in/zoom out\n');

% % 指向你的其中一个数据文件
% file_path = 'N:\matlab_for_gi\data_edited\fast_001_0226.mat'; % 或者是你改名后的任意一个
% info = whos('-file', file_path);
% data_content = load(file_path);
% 
% fprintf('--- 文件中的变量列表 ---\n');
% disp(info); 
% 
% fprintf('--- 变量具体内容预览 ---\n');
% fields = fieldnames(data_content);
% for i = 1:length(fields)
%     val = data_content.(fields{i});
%     if isnumeric(val) && numel(val) == 1
%         fprintf('变量 [%s] 的值是: %f (这很有可能是采样率)\n', fields{i}, val);
%     elseif isstruct(val)
%         fprintf('变量 [%s] 是个结构体，包含字段: %s\n', fields{i}, strjoin(fieldnames(val), ', '));
%     end
% end

% 验证脚本：可视化信号
data_struct = load('N:\matlab_for_gi\data_edited\fast_001_0226.mat'); % 替换为你现有的文件名
vars = struct2cell(data_struct);
[~, idx] = max(cellfun(@numel, vars));
sig = vars{idx};

fs_guess = 200; % 假设是 200Hz
t = (0:length(sig)-1) / fs_guess;

figure;
plot(t, sig);
xlim([100, 160]); % 只看其中 60 秒
xlabel('Time (seconds)');
ylabel('Amplitude (V)');
title('If fs = 200Hz, this is 60 seconds of data');
grid on;