"""Execute revision/main_revision.ipynb with the existing in-process IPython.

The sandbox blocks kernel sockets. This notebook contains ordinary Python cells;
IPython executes them in one shared namespace and captures rich output without
opening sockets or installing nbclient/nbformat. Child stdout is also captured.
"""
import json
import os
from pathlib import Path
import tempfile
import traceback
os.environ.setdefault('IPYTHONDIR','/tmp/weather-revision-ipython')
from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from .protocol import ROOT,REVISION


def main():
    file=REVISION/'main_revision.ipynb';notebook=json.loads(file.read_text())
    os.chdir(ROOT)
    for key in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:os.environ[key]='2'
    os.environ['MPLCONFIGDIR']='/tmp/weather-revision-matplotlib'
    shell=InteractiveShell.instance()
    for number,cell in enumerate(notebook['cells']):
        if cell['cell_type']!='code':continue
        source=''.join(cell['source']);cell['outputs']=[]
        cell['execution_count']=shell.execution_count
        with tempfile.TemporaryFile(mode='w+',encoding='utf-8') as child_output:
            stdout_fd=os.dup(1);stderr_fd=os.dup(2)
            try:
                os.dup2(child_output.fileno(),1);os.dup2(child_output.fileno(),2)
                with capture_output(stdout=True,stderr=True,display=True) as captured:
                    result=shell.run_cell(source,store_history=True)
            finally:
                os.dup2(stdout_fd,1);os.dup2(stderr_fd,2);os.close(stdout_fd);os.close(stderr_fd)
            child_output.seek(0);child_text=child_output.read()
        if captured.stdout or child_text:
            cell['outputs'].append(dict(output_type='stream',name='stdout',text=captured.stdout+child_text))
        if captured.stderr:
            cell['outputs'].append(dict(output_type='stream',name='stderr',text=captured.stderr))
        for output in captured.outputs:
            cell['outputs'].append(dict(output_type='display_data',data=output.data,metadata=output.metadata or {}))
        error=result.error_before_exec or result.error_in_exec
        if error:
            cell['outputs'].append(dict(output_type='error',ename=type(error).__name__,evalue=str(error),
                                        traceback=traceback.format_exception(type(error),error,error.__traceback__)))
        notebook['metadata']['revision_execution']={
            'backend':'existing venv in-process IPython; ordinary Python cells; shared namespace',
            'kernel_sockets_used':False,'expensive_model_fits_replayed':False}
        file.write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n')
        print('Executed revision cell',number,'count',cell['execution_count'],flush=True)
        if error:raise RuntimeError(f'Revision cell {number} failed; inspect saved output') from error
    print('Revision notebook saved with executed outputs',flush=True)


if __name__=='__main__':main()
