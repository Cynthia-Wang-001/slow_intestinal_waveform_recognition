%% 1. 加载数据
data_file = 'N:\matlab_for_gi\20201102-AM-fasting.mat'; 

% 自动获取变量名（以防不叫 data）
vars = fieldnames(raw_data);
data = raw_data.(vars{1}); 

%% 2. 设置截取参数 (根据需要修改这里)
% 如果你想看最开始，设置 start_point = 1
% 如果想看中间，可以参考你之前的图（比如 500,000 左右）
start_point = 500000;  
num_points = 50000;    % 截取一万个点，如果还是太挤，就改成 5000

end_point = start_point + num_points;

% 确保索引不超出数据范围
[total_samples, num_channels] = size(data);
end_point = min(end_point, total_samples);
range = start_point : end_point;

%% 3. 绘图
fig = figure('Color', 'w', 'Name', '局部波形细节观察');

for i = 1:num_channels
    ax(i) = subplot(num_channels, 1, i); % 记录每个子图的句柄，用于后续联动
    
    % 截取数据并去趋势（去除基线漂移，使波形居中）
    segment = data(range, i);
    signal_clean = detrend(segment);
    
    % 绘图
    plot(range, signal_clean, 'LineWidth', 1);
    
    % 视觉优化
    ylabel(['Ch ', num2str(i)]);
    grid on;
    axis tight; 
    
    % 只有最下方的图显示 X 轴编号
    if i < num_channels
        set(gca, 'XTickLabel', []); 
    end
end

xlabel('采样点索引 (Sample Points)');
sgtitle(['波形细节展示：第 ', num2str(start_point), ' 至 ', num2str(end_point), ' 点']);

%% 4. 开启联动缩放 (关键步骤)
% 这样你用鼠标放大任何一个子图的横坐标，其他 5 个通道会同步移动
linkaxes(ax, 'x');

fprintf('脚本运行完成。你可以使用工具栏的放大镜对准某个波峰拉框放大。\n');