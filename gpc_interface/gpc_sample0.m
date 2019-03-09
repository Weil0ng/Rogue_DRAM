function [samplePoints, gpcmodel]=gpc_sample0(model_spec, order)
% model_spec array of array, first ele is param name, followed by dist,
% mean, std

%celldisp(model_spec);
dists = cell(size(model_spec, 2), 1);
pdf_specs = cell(1, size(model_spec, 2));
for p=1:size(model_spec, 2)
    spec = model_spec{p};
    dists{p, 1} = spec{2};
    %pdf_specs{p} = [spec{3}, spec{4}];
    pdf_specs{p} = cell2mat(spec(:, 3:end));
end
%celldisp(pdf_specs);
paraDef.type = dists;
paraDef.pdfPara = pdf_specs;

gpcmodel = modelBuilder(paraDef, order);

gpcmodel.num_Qpoint=round((gpcmodel.pcBasisNum_2p+gpcmodel.pcBasisNum)/2);
[candidate_x,candidate_w] = MCclustering(gpcmodel); 
gpcmodel=candidate_Clustering(candidate_x,candidate_w,gpcmodel); %Clustering

[gpcmodel,resnorm] = weight_solver(gpcmodel); %update W
    %% Increase phase
    increasenum = 3;
    while 1
        info.GNthrethold = 1e-5;
        [gpcmodel,info] = GN_solver(gpcmodel,info); 
        if info.success == 1 
             gpcmodel.QPoints  = gpcmodel.Ini_QPoints ;
             gpcmodel.QWeights = gpcmodel.Ini_QWeights;
             fprintf('Stop Increase phase: M =%3d, res =%4.2e\n',gpcmodel.num_Qpoint,info.res);
            break
        else
         gpcmodel.num_Qpoint = gpcmodel.num_Qpoint + increasenum;
         if gpcmodel.num_Qpoint > gpcmodel.pcBasisNum_2p
             gpcmodel.num_Qpoint = gpcmodel.num_Qpoint - increasenum + 1;
         end
         gpcmodel = candidate_Clustering(candidate_x,candidate_w,gpcmodel); %Ini_QPoints and Ini_QWeight
        end
        fprintf(' Increase phase, M =%3d, res =%4.2e\n',gpcmodel.num_Qpoint,info.res); %res is the one before increasing #
    end 
    %% Decrease phase
    gpcmodel.num_Qpoint = gpcmodel.num_Qpoint - 1;
    while 1        
        [~, minloc] = min(gpcmodel.Ini_QWeights); 
        ind = [1:minloc-1, minloc+1:length(gpcmodel.Ini_QWeights)];
        gpcmodel.Ini_QWeights = gpcmodel.Ini_QWeights(ind);
        gpcmodel.Ini_QWeights = gpcmodel.Ini_QWeights/sum(gpcmodel.Ini_QWeights);
        gpcmodel.Ini_QPoints = gpcmodel.Ini_QPoints(ind,:);
        info.GNthrethold = 1e-5;
        [gpcmodel,info] = GN_solver(gpcmodel,info);
        fprintf(' Decrease phase, M =%3d, res =%4.2e\n',gpcmodel.num_Qpoint,info.res);
        if info.success == 0
           gpcmodel.num_Qpoint = gpcmodel.num_Qpoint + 1;
           fprintf(' Stop Decrease phase: M =%3d\n',gpcmodel.num_Qpoint);
           break; % keep Qpoints, Qweights
        else
            gpcmodel.QPoints  = gpcmodel.Ini_QPoints ;
            gpcmodel.QWeights = gpcmodel.Ini_QWeights;      
            gpcmodel.num_Qpoint = gpcmodel.num_Qpoint - 1;            
        end
    end
gpcmodel.Scaled_SamplePoints = QPoint_scaling(gpcmodel);
samplePoints = gpcmodel.Scaled_SamplePoints;
end


