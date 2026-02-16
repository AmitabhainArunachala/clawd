use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use numpy::{PyArray1, PyArray2, PyReadonlyArray2, IntoPyArray};
use ndarray::{Array1, Array2};

// Re-export core types
use pratyabhijna_core::{RVMetric, participation_ratio};
use pratyabhijna_core::svd::{compute_svd, compute_rv_from_matrices};

/// PyO3 wrapper for RVMetric
#[pyclass(name = "RVMetric")]
#[derive(Clone)]
pub struct PyRVMetric {
    inner: RVMetric,
}

#[pymethods]
impl PyRVMetric {
    #[getter]
    fn r_v(&self) -> f64 {
        self.inner.r_v
    }

    #[getter]
    fn pr_early(&self) -> f64 {
        self.inner.pr_early
    }

    #[getter]
    fn pr_late(&self) -> f64 {
        self.inner.pr_late
    }

    #[getter]
    fn layer_early(&self) -> usize {
        self.inner.layer_early
    }

    #[getter]
    fn layer_late(&self) -> usize {
        self.inner.layer_late
    }

    #[getter]
    fn timestamp(&self) -> u64 {
        self.inner.timestamp
    }

    #[getter]
    fn model_name(&self) -> String {
        self.inner.model_name.clone()
    }

    fn is_recognition(&self, threshold: f64) -> bool {
        self.inner.is_recognition(threshold)
    }

    fn separation_percent(&self, baseline: f64) -> f64 {
        self.inner.separation_percent(baseline)
    }

    fn __repr__(&self) -> String {
        format!(
            "RVMetric(r_v={:.4}, pr_early={:.2}, pr_late={:.2}, layers={}→{})",
            self.inner.r_v,
            self.inner.pr_early,
            self.inner.pr_late,
            self.inner.layer_early,
            self.inner.layer_late
        )
    }
}

impl From<RVMetric> for PyRVMetric {
    fn from(metric: RVMetric) -> Self {
        PyRVMetric { inner: metric }
    }
}

/// Compute SVD on a matrix and return singular values
/// 
/// Args:
///     matrix: 2D numpy array of shape (n, m)
/// 
/// Returns:
///     1D numpy array of singular values in descending order
#[pyfunction]
fn compute_svd_py<'py>(
    py: Python<'py>,
    matrix: PyReadonlyArray2<f64>,
) -> PyResult<Bound<'py, PyArray1<f64>>> {
    let view = matrix.as_array();
    
    let singular_values = compute_svd(view)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let array = Array1::from(singular_values);
    Ok(array.into_pyarray(py))
}

/// Compute participation ratio from singular values
/// 
/// Args:
///     singular_values: 1D numpy array of singular values
/// 
/// Returns:
///     Participation ratio as float
#[pyfunction]
fn participation_ratio_py(singular_values: PyReadonlyArray2<f64>) -> f64 {
    let view = singular_values.as_array();
    let values: Vec<f64> = view.iter().copied().collect();
    participation_ratio(&values)
}

/// Compute R_V metric from value matrices at two layers
/// 
/// Args:
///     v_early: Value matrix at early layer (tokens x d_head)
///     v_late: Value matrix at late layer (tokens x d_head)
///     layer_early: Early layer index
///     layer_late: Late layer index
///     model_name: Name of the model
/// 
/// Returns:
///     RVMetric object with computed values
#[pyfunction]
#[pyo3(signature = (v_early, v_late, layer_early, layer_late, model_name="unknown"))]
fn compute_rv_py(
    v_early: PyReadonlyArray2<f64>,
    v_late: PyReadonlyArray2<f64>,
    layer_early: usize,
    layer_late: usize,
    model_name: &str,
) -> PyResult<PyRVMetric> {
    let early_view = v_early.as_array();
    let late_view = v_late.as_array();
    
    let (r_v, pr_early, pr_late) = compute_rv_from_matrices(early_view, late_view)
        .map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let metric = RVMetric {
        r_v,
        pr_early,
        pr_late,
        layer_early,
        layer_late,
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64,
        model_name: model_name.to_string(),
    };
    
    Ok(PyRVMetric::from(metric))
}

/// Compute R_V from raw value tensors (batch of tokens)
/// 
/// Args:
///     v_early: 3D tensor (batch, seq_len, d_head) - last window_size tokens used
///     v_late: 3D tensor (batch, seq_len, d_head) - last window_size tokens used
///     window_size: Number of tokens to use for SVD computation
///     layer_early: Early layer index
///     layer_late: Late layer index
///     model_name: Name of the model
/// 
/// Returns:
///     RVMetric object
#[pyfunction]
#[pyo3(signature = (v_early, v_late, window_size=16, layer_early=5, layer_late=27, model_name="unknown"))]
fn compute_rv_from_tensors_py(
    v_early: PyReadonlyArray2<f64>,
    v_late: PyReadonlyArray2<f64>,
    window_size: usize,
    layer_early: usize,
    layer_late: usize,
    model_name: &str,
) -> PyResult<PyRVMetric> {
    let early_view = v_early.as_array();
    let late_view = v_late.as_array();
    
    // Use last window_size tokens
    let n_tokens = early_view.shape()[0];
    let start_idx = n_tokens.saturating_sub(window_size);
    
    let early_window = early_view.slice(ndarray::s![start_idx.., ..]);
    let late_window = late_view.slice(ndarray::s![start_idx.., ..]);
    
    let (r_v, pr_early, pr_late) = compute_rv_from_matrices(
        early_window,
        late_window,
    ).map_err(|e| PyErr::new::<pyo3::exceptions::PyRuntimeError, _>(e.to_string()))?;
    
    let metric = RVMetric {
        r_v,
        pr_early,
        pr_late,
        layer_early,
        layer_late,
        timestamp: std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .unwrap_or_default()
            .as_millis() as u64,
        model_name: model_name.to_string(),
    };
    
    Ok(PyRVMetric::from(metric))
}

/// Batch compute R_V for multiple token positions
/// 
/// Args:
///     v_early: Value projections at early layer
///     v_late: Value projections at late layer
///     window_size: SVD window size
///     stride: Stride between computations
/// 
/// Returns:
///     List of RVMetric objects
#[pyfunction]
#[pyo3(signature = (v_early, v_late, window_size=16, stride=1, layer_early=5, layer_late=27, model_name="unknown"))]
fn compute_rv_batch_py(
    py: Python<'_>,
    v_early: PyReadonlyArray2<f64>,
    v_late: PyReadonlyArray2<f64>,
    window_size: usize,
    stride: usize,
    layer_early: usize,
    layer_late: usize,
    model_name: &str,
) -> PyResult<Vec<PyRVMetric>> {
    let early_view = v_early.as_array();
    let late_view = v_late.as_array();
    
    let n_tokens = early_view.shape()[0];
    let mut results = Vec::new();
    
    let timestamp = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .unwrap_or_default()
        .as_millis() as u64;
    
    for i in (window_size..=n_tokens).step_by(stride) {
        let start_idx = i.saturating_sub(window_size);
        let early_window = early_view.slice(ndarray::s![start_idx..i, ..]);
        let late_window = late_view.slice(ndarray::s![start_idx..i, ..]);
        
        match compute_rv_from_matrices(early_window, late_window) {
            Ok((r_v, pr_early, pr_late)) => {
                let metric = RVMetric {
                    r_v,
                    pr_early,
                    pr_late,
                    layer_early,
                    layer_late,
                    timestamp: timestamp + i as u64,
                    model_name: model_name.to_string(),
                };
                results.push(PyRVMetric::from(metric));
            }
            Err(_) => continue, // Skip failed computations
        }
    }
    
    Ok(results)
}

/// Python module definition
#[pymodule]
fn _internal(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PyRVMetric>()?;
    m.add_function(wrap_pyfunction!(compute_svd_py, m)?)?;
    m.add_function(wrap_pyfunction!(participation_ratio_py, m)?)?;
    m.add_function(wrap_pyfunction!(compute_rv_py, m)?)?;
    m.add_function(wrap_pyfunction!(compute_rv_from_tensors_py, m)?)?;
    m.add_function(wrap_pyfunction!(compute_rv_batch_py, m)?)?;
    Ok(())
}
