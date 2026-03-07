% input_dir = 'N:\data_part2\new_2_edited';
% output_dir = 'N:\data_part2\new_segmented';
% 
% if ~exist(output_dir, 'dir'), mkdir(output_dir); end
% 
% fs = 200; 
% noise_threshold = 2.0;
% cut_sec = 10;
% segment_len = 100000;
% [b, a] = butter(2, [0.05, 1.5] / (fs/2), 'bandpass');
% 
% files = dir(fullfile(input_dir, '*.mat'));
% log_data = {}; 
% 
% for i = 1:length(files)
%     fprintf('Processing: %s\n', files(i).name);
%     load_struct = load(fullfile(input_dir, files(i).name));
%     raw_matrix = load_struct.data; % 直接提取 [960507 x 6] 的矩阵
% 
%     num_channels = size(raw_matrix, 2); % 应该是 6
%     [~, base_name, ~] = fileparts(files(i).name);
% 
%     for ch = 1:num_channels
%         % 提取单个通道
%         single_ch = raw_matrix(:, ch);
% 
%         % 1. 去噪 (限幅插值)
%         single_ch(abs(single_ch) > noise_threshold) = NaN;
%         single_ch = fillmissing(single_ch, 'linear');
% 
%         % 2. 滤波
%         filtered = filtfilt(b, a, single_ch);
% 
%         % 3. 切头尾
%         pts_to_cut = cut_sec * fs;
%         if length(filtered) <= 2 * pts_to_cut, continue; end
%         trimmed = filtered(pts_to_cut+1 : end-pts_to_cut);
% 
%         % 4. 切分
%         num_segs = floor(length(trimmed) / segment_len);
%         for s = 1:num_segs
%             start_idx = (s-1) * segment_len + 1;
%             end_idx = s * segment_len;
%             segment_data = trimmed(start_idx : end_idx);
% 
%             % 【新命名逻辑】：文件名_Ch通道号_seg段号
%             new_filename = sprintf('%s_Ch%d_seg%02d.mat', base_name, ch, s);
%             save(fullfile(output_dir, new_filename), 'segment_data', 'fs');
% 
%             % 记录日志
%             start_t = (start_idx + pts_to_cut - 1) / fs;
%             end_t = (end_idx + pts_to_cut - 1) / fs;
%             log_data(end+1, :) = {new_filename, files(i).name, ch, s, start_t, end_t};
%         end
%     end
% end
% 
% % 保存索引表
% T = cell2table(log_data, 'VariableNames', {'File', 'Source', 'Channel', 'Segment', 'Start_Sec', 'End_Sec'});
% writetable(T, fullfile(output_dir, 'Processing_Log.xlsx'));
% fprintf('Done! 6 channels processed individually.\n');
% 
% input_dir = 'N:\data_part2\new_2_edited';
% output_dir = 'N:\data_part2\new_segmented';
% 
% if ~exist(output_dir, 'dir'), mkdir(output_dir); end
% 
% fs = 200; 
% noise_threshold = 2.0;
% cut_sec = 10;
% segment_len = 100000;
% [b, a] = butter(2, [0.05, 1.5] / (fs/2), 'bandpass');
% 
% % --- 修改部分：文件名序列筛选 ---
% all_files = dir(fullfile(input_dir, '*.mat'));
% keep_idx = [];
% 
% for k = 1:length(all_files)
%     fname = all_files(k).name;
%     % 匹配文件名中的前缀和数字部分 (例如 fast_055_0305 -> tokens: {'fast', '055'})
%     tokens = regexp(fname, '^(fast|postprandial)_(\d+)_', 'tokens');
% 
%     if ~isempty(tokens)
%         type = tokens{1}{1};      % 前缀: fast 或 postprandial
%         num = str2double(tokens{1}{2}); % 中间的编号数字
% 
%         % 判断是否在指定范围内
%         if strcmp(type, 'fast') && (num >= 22 && num <= 59)
%             keep_idx(end+1) = k;
%         elseif strcmp(type, 'postprandial') && (num >= 14 && num <= 37)
%             keep_idx(end+1) = k;
%         end
%     end
% end
% files = all_files(keep_idx); % 仅保留符合范围的文件
% % ------------------------------
% 
% log_data = {}; 
% 
% for i = 1:length(files)
%     fprintf('Processing: %s\n', files(i).name);
%     % ... 以下逻辑保持不变 ...
%     load_struct = load(fullfile(input_dir, files(i).name));
% 
%     % 注意：如果你的.mat文件内部变量名不是 'data'，请根据实际情况修改下一行
%     raw_matrix = load_struct.data; 
% 
%     num_channels = size(raw_matrix, 2); 
%     [~, base_name, ~] = fileparts(files(i).name);
% 
%     for ch = 1:num_channels
%         single_ch = raw_matrix(:, ch);
% 
%         % 1. 去噪
%         single_ch(abs(single_ch) > noise_threshold) = NaN;
%         single_ch = fillmissing(single_ch, 'linear');
% 
%         % 2. 滤波
%         filtered = filtfilt(b, a, single_ch);
% 
%         % 3. 切头尾
%         pts_to_cut = cut_sec * fs;
%         if length(filtered) <= 2 * pts_to_cut, continue; end
%         trimmed = filtered(pts_to_cut+1 : end-pts_to_cut);
% 
%         % 4. 切分
%         num_segs = floor(length(trimmed) / segment_len);
%         for s = 1:num_segs
%             start_idx = (s-1) * segment_len + 1;
%             end_idx = s * segment_len;
%             segment_data = trimmed(start_idx : end_idx);
% 
%             new_filename = sprintf('%s_Ch%d_seg%02d.mat', base_name, ch, s);
%             save(fullfile(output_dir, new_filename), 'segment_data', 'fs');
% 
%             start_t = (start_idx + pts_to_cut - 1) / fs;
%             end_t = (end_idx + pts_to_cut - 1) / fs;
%             log_data(end+1, :) = {new_filename, files(i).name, ch, s, start_t, end_t};
%         end
%     end
% end
% 
% % 保存索引表
% if ~isempty(log_data)
%     T = cell2table(log_data, 'VariableNames', {'File', 'Source', 'Channel', 'Segment', 'Start_Sec', 'End_Sec'});
%     writetable(T, fullfile(output_dir, 'Processing_Log.xlsx'));
% end
% fprintf('Done! Specified range processed.\n');

%% 初始化路径与参数
input_dir = 'N:\data_part2\new_2_edited';
output_dir = 'N:\data_part2\new_segmented_post'; 

if ~exist(output_dir, 'dir'), mkdir(output_dir); end

fs = 200; 
noise_threshold = 2.0;
cut_sec = 10;
segment_len = 100000;
[b, a] = butter(2, [0.05, 1.5] / (fs/2), 'bandpass');

%% 筛选 postprandial 014-037 的文件
all_files = dir(fullfile(input_dir, 'postprandial_*.mat'));
keep_idx = [];

for k = 1:length(all_files)
    fname = all_files(k).name;
    tokens = regexp(fname, '^postprandial_(\d+)_', 'tokens');
    if ~isempty(tokens)
        num = str2double(tokens{1}{1});
        if num >= 14 && num <= 37
            keep_idx(end+1) = k;
        end
    end
end

files = all_files(keep_idx);
fprintf('找到符合范围的 Postprandial 文件共: %d 个\n', length(files));

%% 循环处理
log_data = {}; 

for i = 1:length(files)
    % 提取当前循环的文件名，确保在 try 块内外都能访问
    this_file_name = files(i).name; 
    
    try
        fprintf('Processing (%d/%d): %s\n', i, length(files), this_file_name);
        
        % 1. check the size of file
        if files(i).bytes < 10240 
            warning('跳过损坏文件 (大小异常): %s', this_file_name);
            continue;
        end

        % 2. load data
        load_struct = load(fullfile(input_dir, this_file_name));
        
        % check variable name (if is data or not)
        if ~isfield(load_struct, 'data')
            warning('文件 %s 中未找到 data 变量，尝试直接读取内容...', this_file_name);
            % if not data，first variable in construct
            fields = fieldnames(load_struct);
            if isempty(fields), continue; end
            raw_matrix = load_struct.(fields{1});
        else
            raw_matrix = load_struct.data; 
        end
        
        % save
        [~, base_name, ~] = fileparts(this_file_name);
        num_channels = size(raw_matrix, 2); 
        
        % 3. process channel by channel
        for ch = 1:num_channels
            single_ch = raw_matrix(:, ch);
            
            % remove noise
            single_ch(abs(single_ch) > noise_threshold) = NaN;
            single_ch = fillmissing(single_ch, 'linear');
            
            % filter
            filtered = filtfilt(b, a, single_ch);
            
            % cut head and tail signals(also remove noise)
            pts_to_cut = cut_sec * fs;
            if length(filtered) <= 2 * pts_to_cut, continue; end
            trimmed = filtered(pts_to_cut+1 : end-pts_to_cut);
            
            % cut in small segmentation
            num_segs = floor(length(trimmed) / segment_len);
            for s = 1:num_segs
                start_idx = (s-1) * segment_len + 1;
                end_idx = s * segment_len;
                segment_data = trimmed(start_idx : end_idx);
                
                % 保存
                new_filename = sprintf('%s_Ch%d_seg%02d.mat', base_name, ch, s);
                save(fullfile(output_dir, new_filename), 'segment_data', 'fs');
                
                % 计算时间并记录日志
                start_t = (start_idx + pts_to_cut - 1) / fs;
                end_t = (end_idx + pts_to_cut - 1) / fs;
                log_data(end+1, :) = {new_filename, this_file_name, ch, s, start_t, end_t};
            end
        end
        
    catch ME
        fprintf('处理 %s 时发生错误，错误原因: %s\n', this_file_name, ME.message);
        continue; 
    end
end

%% 保存日志
if ~isempty(log_data)
    T = cell2table(log_data, 'VariableNames', {'File', 'Source', 'Channel', 'Segment', 'Start_Sec', 'End_Sec'});
    writetable(T, fullfile(output_dir, 'Postprandial_Processing_Log.xlsx'));
    fprintf('全部处理完成！\n');
else
    fprintf('未生成任何有效数据，请检查原始 .mat 文件内容。\n');
end