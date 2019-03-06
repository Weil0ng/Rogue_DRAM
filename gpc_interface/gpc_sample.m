function [samplePoints, model]=gpc_sample(model_spec, order)
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

model = modelBuilder(paraDef, order);
samplePoints = model.Scaled_SamplePoints;
end


