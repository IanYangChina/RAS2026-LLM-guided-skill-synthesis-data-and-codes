## Search State

- **Seed**: 4
- **Iteration**: 15 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 14 | approach → descend → push → retract | linear_cartesian | linear_cartesian | impedance_motion | linear_cartesian | position_control | impedance_control | impedance_control | position_control | pose_tolerance | contact_detected | time_limit | pose_tolerance | 5 | -0.1881 | 0.00 | ❌ rejected |
| 13 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4177 | 0.79 | ❌ rejected |
| 12 | approach → descend → push | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | pose_tolerance | force_exceeded | time_limit | 4 | 0.7835 | 0.35 | ❌ rejected |
| 11 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4171 | 0.80 | ❌ rejected |
| 10 | push → align → release → insert | impedance_motion | linear_cartesian | linear_cartesian | impedance_motion | impedance_control | position_control | admittance_control | impedance_control | time_limit | pose_tolerance | pose_tolerance | force_exceeded | 6 | 0.4187 | 0.80 | ❌ rejected |

**Proposal policy**: task_score is 0.00 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
- task_score stagnant: change coupled targets, parameters, terminations, phase types, controls, subtasks, or ordering when evidence shows they need to change together.
A HOLD wastes an iteration when task_score is below 0.9.

## Optimisation Objective

Your goal is to **maximise task_score first, then composite score Q**:

> **Primary objective: task_score** — the fraction of episodes where the robot successfully completes the task. This is the most important metric. **Never propose a simpler or shorter skill if it reduces task_score.**

> **Q = fitness_score + termination_fidelity − complexity_penalty**

- `fitness_score`: shaped task reward (includes phase progress for contact-rich tasks)
- `termination_fidelity`: fraction of phases that terminated by designed condition (not timeout)
- `complexity_penalty`: cost for over-parameterised or over-phased designs

**Warning**: Do not reduce phases or parameters to lower complexity if doing so reduces task_score. Structure complexity is only penalised when it adds no performance gain.

# Proposal Context

## Task Specification

- Task name: push_to_goal
- Frozen realised-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`
- Frozen object start: [0.5531667326686841, 0.0013593063377233885, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.5531667326686841, 0.0013593063377233885, 0.025)
- Goal tolerance: 0.02 m
- Expressivity sigma: 1.0 m
- Expressivity threshold: 0.8
- Force limit: 25.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **object displacement ratio toward goal_object_position**

## Scene Entities

robot:
  model: panda_pusher
  tcp_site: attachment_site
  gripper: null
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: push_box
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.05, 0.05, 0.05]
    mass_kg: 0.1
  - name: goal_marker
    role: target_marker
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.5532, 0.0014, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.5531667326686841, 0.0013593063377233885, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [-0.0532, -0.1514, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 0.839, which indicates the subtask decomposition is already effective.
> Preserve the current subtask decomposition unless the evidence shows a subtask change is necessary. Prefer refining phases, parameters, control modes, or termination conditions first.
> Unnecessary subtask redesign when performance is already high often causes regression.

## Subtask Layer

**Mode**: free (you define subtask targets; use `subtasks:` block in your YAML)

Define subtasks in a `subtasks:` block **before** `phases:`. Each subtask specifies an intermediate optimisation target.

**Required fields** — always include both, never omit:
- `anchor` (**required**): fixture | goal | object | world
- `target_entity` (**required**): hinge | object | tcp

Subtask anchors are separate from phase `target.anchor` vocabulary: subtasks use `world | object | goal | fixture`, while phase targets use `world | task_goal | task_object | fixture | body | site | current_tcp`.

Optional fields:
- `metric`: contact | distance | goal_progress | hinge_angle (default: distance)
- `offset`: [x, y, z] in metres relative to anchor (default: [0, 0, 0])
- `param_offset_key`: CMA-ES parameter added to offset at runtime (optional)
- `weight`: scoring weight [0.1, 1.0] (default: 1.0)

**Anchor resolution for this task** — choose anchor so the resolved position is meaningful:
| Anchor | Resolves to | Best used for |
|--------|-------------|---------------|
| `world` | absolute world-frame coordinate | fixed reference points not tied to objects |
| `object` | offset from object initial position (0.5531667326686841, 0.0013593063377233885, 0.025) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.5, -0.15, 0.025) | final destination targets |
| `fixture` | offset from fixture pose (if defined, else world) | targets near fixture |

Annotate each phase with `subtask_id: <id>` to bind it to a subtask.
Only the **last phase** bound to a given subtask contributes to subtask scoring.

Example (two subtasks — one near object start, one at goal):
```yaml
subtasks:
  - id: reach_pre_contact
    anchor: object         # resolved to object initial position (see table above)
    target_entity: tcp     # score TCP distance to this target
    metric: distance
    offset: [0.0, 0.0, 0.10]  # 10 cm above object start position
    weight: 0.3
  - id: reach_goal
    anchor: goal           # resolved to task goal position (see table above)
    target_entity: tcp
    metric: distance
    offset: [0.0, 0.0, 0.0]
    weight: 0.7
phases:
  - id: approach_1
    type: approach
    subtask_id: reach_pre_contact
    ...
  - id: push_1
    type: push
    subtask_id: reach_goal
    ...
```

## Current Skill (Q=-0.188) — your mutation base

```yaml
skill: push_to_goal
skill_type: arm_gripper
phases:
- id: push_1
  type: push
  generator: impedance_motion
  control: impedance_control
  termination: time_limit
  parameters:
    push_distance:
      type: scalar
      range:
      - 0.02
      - 0.2
    push_speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: align_1
  type: align
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    lateral_offset_x:
      type: scalar
      range:
      - -0.01
      - 0.01
    lateral_offset_y:
      type: scalar
      range:
      - -0.01
      - 0.01
- id: release_1
  type: release
  generator: linear_cartesian
  control: admittance_control
  termination: pose_tolerance
  end_effector_action: open
- id: insert_1
  type: insert
  generator: impedance_motion
  control: impedance_control
  termination: force_exceeded
  parameters:
    insertion_depth:
      type: scalar
      range:
      - 0.01
      - 0.15
    insertion_force:
      type: scalar
      range:
      - 1.0
      - 20.0

```

## Design Metrics

- **Composite score**: -0.188
- **task_score** (E): 0.000
- **fitness_score**: 0.122  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.310

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach | 1.00 | 1.00 | 0.1815 |
| descend | 1.00 | 1.00 | 0.0811 |
| push | 0.00 | 1.00 | 0.0001 |
| retract | 1.00 | 1.00 | 0.0884 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.525, 0.006, 0.123) | (0.531, 0.007, 0.025)→(0.531, 0.007, 0.025) | 0.161→0.161 | 1.00 / 3.000 | 67.406 | 237.560 |
| descend | descend | 1.00 / step_budget | (0.525, 0.006, 0.123)→(0.547, 0.006, 0.045) | (0.531, 0.007, 0.025)→(0.537, 0.007, 0.024) | 0.161→0.162 | 1.00 / 4.333 | 116.913 | 117.314 |
| push | push | 0.00 / guard_failure | (0.547, 0.006, 0.045)→(0.547, 0.006, 0.045) | (0.537, 0.007, 0.024)→(0.537, 0.007, 0.024) | 0.162→0.162 | 1.00 / 4.000 | 0.245 | 122.887 |
| retract | retract | 1.00 / step_budget | (0.547, 0.006, 0.045)→(0.543, 0.006, 0.133) | (0.537, 0.007, 0.024)→(0.535, 0.007, 0.025) | 0.162→0.162 | 1.00 / 4.000 | 0.245 | 0.245 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 0.030
- lateral_force_integral: None
- approach_alignment: 0.555
- goal_progress: 0.001
- terminal_score: 0.001
- phase_score: 0.203
- phase_breakdown.reach_object_score: 0.677
- phase_breakdown.goal_progress_score: 0.000

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.122
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.001
- **Median Q (composite search score)**: -0.188
- **K-run variance**: 0.0000
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 9.0
- **Final σ (mean)**: 0.298


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `8d5a7e825d9524a0954b44a69bda19e1d764760f64bb1262d03aec3c389fadbb`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c4094dd933e0897d422d7ea261a82b80810f7dec183b19c1da5b940157e7d0c4`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.59494,"average_solve_count":79.0,"average_success_count":79.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.20872,"descend.descend_speed":0.05843,"push.push_distance":0.16293,"push.push_speed":0.0403,"retract.retract_speed":0.11392},"optimized_scores":{"best_composite_score":-0.1882,"best_fitness_score":0.1218,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":257.0,"contact_point_centroid":[0.56818,0.00128,0.04724],"force_p95":229.12623,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":229.79326,"mean_force":172.49494,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.55635,0.00122,0.04786]},{"body_a":"attachment","body_b":"push_box","contact_count":42.0,"contact_point_centroid":[0.57838,0.00128,0.04795],"force_p95":66.90935,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.65678,"mean_force":20.47623,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.5665,0.00125,0.04864]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.57889,0.0013,0.04574],"force_p95":116.83559,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.93639,"mean_force":112.92752,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.56693,0.00126,0.0453]},{"body_a":"world","body_b":"push_box","contact_count":2661.0,"contact_point_centroid":[0.55414,0.00135,-0.00017],"force_p95":98.63301,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":115.47904,"mean_force":16.96981,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.54853,0.00116,0.07071]},{"body_a":"world","body_b":"push_box","contact_count":2015.0,"contact_point_centroid":[0.55801,0.00134,-3e-05],"force_p95":0.29813,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":62.14044,"mean_force":0.67643,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.56363,0.00117,0.08866]},{"body_a":"world","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.56258,0.00138,-0.00067],"force_p95":59.2483,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.95186,"mean_force":34.19208,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.56694,0.00126,0.04531]},{"body_a":"world","body_b":"push_box","contact_count":1316.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.52114,0.00055,0.21224]}],"total_contact_groups":7},"final_pose_error":0.01341,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.55745,0.00136,0.02499],"final_tcp_position":[0.56359,0.00118,0.13242],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":229.79326,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":329.0,"n_steps_budget":630.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.01352,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2918.0,"raw_peak_contact_force":229.79326,"subtask_id":"reach_object","tcp_end":[0.54418,0.00112,0.12234],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09777,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":667.0,"n_steps_budget":1000.0,"object_pos_end":[0.55869,0.00138,0.02388],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.16236,"object_to_goal_dist_start":0.16043,"object_z_max":0.02499,"peak_contact_force":116.93639,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13.0,"raw_peak_contact_force":116.93639,"tcp_end":[0.56688,0.00126,0.04528],"tcp_start":[0.54418,0.00112,0.12234],"tcp_to_object_dist_end":0.02292,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.55868,0.00138,0.02386],"object_pos_start":[0.55869,0.00138,0.02388],"object_to_goal_dist_end":0.16236,"object_to_goal_dist_start":0.16236,"object_z_max":0.02388,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2057.0,"raw_peak_contact_force":121.65678,"subtask_id":"goal_progress","tcp_end":[0.56704,0.00126,0.04538],"tcp_start":[0.56698,0.00126,0.04533],"tcp_to_object_dist_end":0.02309,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.55745,0.00136,0.02499],"object_pos_start":[0.55866,0.00138,0.02387],"object_to_goal_dist_end":0.16189,"object_to_goal_dist_start":0.16235,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1316.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.56359,0.00118,0.13242],"tcp_start":[0.56704,0.00126,0.04538],"tcp_to_object_dist_end":0.1076,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `452b4d03bf1b69f7d6475210c4cc0fbd85197208ecbf5594cd2cfcf54c82bcbb`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":4.0411,"average_solve_count":73.0,"average_success_count":73.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.19058,"descend.descend_speed":0.0761,"push.push_distance":0.23874,"push.push_speed":0.10636,"retract.retract_speed":0.11015},"optimized_scores":{"best_composite_score":-0.18825,"best_fitness_score":0.12175,"best_task_score":0.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":196.0,"contact_point_centroid":[0.55137,0.03612,0.04715],"force_p95":238.19792,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":238.67788,"mean_force":182.97523,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53953,0.03609,0.04772]},{"body_a":"attachment","body_b":"push_box","contact_count":42.0,"contact_point_centroid":[0.56076,0.03702,0.0479],"force_p95":65.50368,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":125.41243,"mean_force":21.04389,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54888,0.03712,0.0486]},{"body_a":"world","body_b":"push_box","contact_count":2271.0,"contact_point_centroid":[0.53727,0.03705,-0.00015],"force_p95":111.20651,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":119.84837,"mean_force":16.11247,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.53233,0.03451,0.07251]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.56126,0.03698,0.04564],"force_p95":118.16185,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":118.28215,"mean_force":113.83985,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54931,0.03715,0.04521]},{"body_a":"world","body_b":"push_box","contact_count":2015.0,"contact_point_centroid":[0.54092,0.03739,-3e-05],"force_p95":0.3088,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":64.00541,"mean_force":0.68827,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.54609,0.03687,0.08887]},{"body_a":"world","body_b":"push_box","contact_count":10.0,"contact_point_centroid":[0.54547,0.03746,-0.0007],"force_p95":59.38191,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":59.90411,"mean_force":34.4728,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.54932,0.03715,0.04521]},{"body_a":"world","body_b":"push_box","contact_count":1332.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.51397,0.01575,0.2124]}],"total_contact_groups":7},"final_pose_error":0.01308,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.54036,0.0374,0.02499],"final_tcp_position":[0.54604,0.03687,0.13265],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":238.67788,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":333.0,"n_steps_budget":690.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.0139,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2467.0,"raw_peak_contact_force":238.67788,"subtask_id":"reach_object","tcp_end":[0.52957,0.03241,0.12267],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.09804,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":5.0,"n_steps":568.0,"n_steps_budget":810.0,"object_pos_end":[0.5416,0.03745,0.02384],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.19201,"object_to_goal_dist_start":0.1905,"object_z_max":0.02499,"peak_contact_force":117.07908,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":13.0,"raw_peak_contact_force":118.28215,"tcp_end":[0.54926,0.03714,0.04519],"tcp_start":[0.52957,0.03241,0.12267],"tcp_to_object_dist_end":0.02268,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.54158,0.03745,0.02382],"object_pos_start":[0.5416,0.03745,0.02384],"object_to_goal_dist_end":0.19201,"object_to_goal_dist_start":0.19201,"object_z_max":0.02384,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2057.0,"raw_peak_contact_force":125.41243,"subtask_id":"goal_progress","tcp_end":[0.54941,0.03716,0.04528],"tcp_start":[0.54935,0.03715,0.04523],"tcp_to_object_dist_end":0.02285,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":515.0,"n_steps_budget":600.0,"object_pos_end":[0.54036,0.0374,0.02499],"object_pos_start":[0.54155,0.03745,0.02381],"object_to_goal_dist_end":0.19169,"object_to_goal_dist_start":0.192,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1332.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54604,0.03687,0.13265],"tcp_start":[0.54941,0.03716,0.04528],"tcp_to_object_dist_end":0.10781,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `e3aaa9b30183e782395a479a1824f41a69a2557638e862a63e7a5368dd2a464a`; realized-scene SHA-256: `5f9daa62d5a7a2b8a7116f2dfbb5f9857bb0d5d4b297d304a4e76a9a270e7ec7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.50458,-0.01881,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.00458,-0.13119,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.50458,-0.01881,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.36,"average_solve_count":100.0,"average_success_count":100.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach.approach_speed":0.16919,"descend.descend_speed":0.05808,"push.push_distance":0.18494,"push.push_speed":0.10289,"retract.retract_speed":0.05873},"optimized_scores":{"best_composite_score":-0.18776,"best_fitness_score":0.12224,"best_task_score":0.001},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":251.0,"contact_point_centroid":[0.52131,-0.01839,0.04702],"force_p95":242.49753,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":244.20879,"mean_force":182.23601,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50985,-0.01859,0.04739]},{"body_a":"world","body_b":"push_box","contact_count":2584.0,"contact_point_centroid":[0.50601,-0.01886,-0.00017],"force_p95":108.55873,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":150.44674,"mean_force":18.0109,"phase_index":1.0,"phase_name":"descend","phase_type":"descend","tcp_position_centroid":[0.50267,-0.0177,0.07266]},{"body_a":"attachment","body_b":"push_box","contact_count":51.0,"contact_point_centroid":[0.53536,-0.01855,0.04781],"force_p95":80.69724,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":121.59154,"mean_force":25.92982,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52337,-0.0192,0.04799]},{"body_a":"attachment","body_b":"push_box","contact_count":3.0,"contact_point_centroid":[0.5355,-0.01686,0.04545],"force_p95":115.76955,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":116.7239,"mean_force":105.70262,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52365,-0.01917,0.04427]},{"body_a":"world","body_b":"push_box","contact_count":3580.0,"contact_point_centroid":[0.50929,-0.01913,-3e-05],"force_p95":0.24603,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":66.3322,"mean_force":0.62271,"phase_index":3.0,"phase_name":"retract","phase_type":"retract","tcp_position_centroid":[0.52037,-0.01914,0.09223]},{"body_a":"world","body_b":"push_box","contact_count":6.0,"contact_point_centroid":[0.53344,-0.01921,-0.00104],"force_p95":62.50967,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":63.77818,"mean_force":53.40189,"phase_index":2.0,"phase_name":"push","phase_type":"push","tcp_position_centroid":[0.52365,-0.01917,0.04427]},{"body_a":"world","body_b":"push_box","contact_count":1284.0,"contact_point_centroid":[0.50458,-0.01881,-1e-05],"force_p95":0.24531,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach","phase_type":"approach","tcp_position_centroid":[0.50023,-0.00797,0.21346]}],"total_contact_groups":7},"final_pose_error":0.00997,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.50845,-0.01913,0.02499],"final_tcp_position":[0.52049,-0.01913,0.13489],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.50458,-0.01881,0.025]},"peak_contact_force":244.20879,"phases":[{"contact_detected":true,"contact_event_count":3.0,"n_steps":321.0,"n_steps_budget":750.0,"object_pos_end":[0.50458,-0.01881,0.02499],"object_pos_start":[0.50458,-0.01881,0.025],"object_to_goal_dist_end":0.13127,"object_to_goal_dist_start":0.13127,"object_z_max":0.025,"peak_contact_force":202.19066,"phase_name":"approach","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":2835.0,"raw_peak_contact_force":244.20879,"subtask_id":"reach_object","tcp_end":[0.50137,-0.01648,0.12411],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.0992,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":666.0,"n_steps_budget":1000.0,"object_pos_end":[0.51147,-0.01905,0.02561],"object_pos_start":[0.50458,-0.01881,0.02499],"object_to_goal_dist_end":0.13145,"object_to_goal_dist_start":0.13127,"object_z_max":0.02578,"peak_contact_force":116.7239,"phase_name":"descend","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":9.0,"raw_peak_contact_force":116.7239,"tcp_end":[0.52359,-0.01916,0.04428],"tcp_start":[0.50137,-0.01648,0.12411],"tcp_to_object_dist_end":0.02226,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":3.0,"n_steps_budget":1000.0,"object_pos_end":[0.51145,-0.01906,0.0256],"object_pos_start":[0.51147,-0.01905,0.02561],"object_to_goal_dist_end":0.13144,"object_to_goal_dist_start":0.13145,"object_z_max":0.02561,"peak_contact_force":0.24525,"phase_name":"push","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3631.0,"raw_peak_contact_force":121.59154,"subtask_id":"goal_progress","tcp_end":[0.52376,-0.01918,0.04431],"tcp_start":[0.52371,-0.01918,0.04427],"tcp_to_object_dist_end":0.02239,"terminated_normally":false,"termination_reason":"guard_failure"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":925.0,"n_steps_budget":1000.0,"object_pos_end":[0.50845,-0.01913,0.02499],"object_pos_start":[0.51142,-0.01907,0.02562],"object_to_goal_dist_end":0.13114,"object_to_goal_dist_start":0.13143,"object_z_max":0.02621,"peak_contact_force":0.24525,"phase_name":"retract","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":1284.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.52049,-0.01913,0.13489],"tcp_start":[0.52376,-0.01918,0.04431],"tcp_to_object_dist_end":0.11056,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```