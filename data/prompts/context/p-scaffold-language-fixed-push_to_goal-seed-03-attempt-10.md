## Search State

- **Seed**: 3
- **Iteration**: 11 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 10 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4794 | 0.72 | ❌ rejected |
| 9 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 6 | -0.2082 | 0.02 | ❌ rejected |
| 8 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | force_exceeded | pose_tolerance | 4 | 0.2665 | 0.04 | ❌ rejected |
| 7 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4540 | 0.64 | ❌ rejected |
| 6 | approach → contact → push → retract | linear_cartesian | linear_cartesian | linear_cartesian | linear_cartesian | position_control | force_threshold_switch | impedance_control | position_control | pose_tolerance | contact_detected | pose_tolerance | pose_tolerance | 3 | 0.4710 | 0.73 | ❌ rejected |

**Proposal policy**: task_score is 0.72 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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
- Frozen realised-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`
- Frozen object start: [0.45027790005723495, -0.03158273920846803, 0.025]
- Frozen task target: [0.5, -0.15, 0.025]
- Goal object position: (0.5, -0.15, 0.025)
- Object initial pose: (0.45027790005723495, -0.03158273920846803, 0.025)
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
  frozen_object_start: [0.4503, -0.0316, 0.025]
  frozen_task_target: [0.5, -0.15, 0.025]
  frozen_object_starts: {'push_box': [0.45027790005723495, -0.03158273920846803, 0.025]}
  frozen_targets: {'task_goal': [0.5, -0.15, 0.025]}
  push_direction: [0.0497, -0.1184, 0]
  goal_tolerance_m: 0.02
  force_limit_n: 25
  force_scale_n: 5
  realized_scene_sha256: 35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be

## Subtask Layer

**Mode**: fixed (subtask targets are defined by the task configuration)

Available subtask IDs for phase binding:
| Subtask ID | Anchor | Target offset (m) | Metric | CMA-ES offset param |
|---|---|---|---|---|
| approach | object | (0.00, 0.08, 0.00) | distance | — |
| contact | object | (0.00, 0.03, 0.00) | distance | — |
| push | goal | (0.00, 0.03, 0.00) | distance | push_depth |

Annotate phases with `subtask_id: <id>` to bind them to a subtask target.
- A phase bound to a subtask receives a navigation waypoint computed from that subtask's anchor and offset.
- Only the **last phase** bound to a given subtask is used for subtask scoring.
- Phases without `subtask_id` are not scored against subtasks but still execute normally.

## Current Skill (Q=0.479) — your mutation base

```yaml
skill: push_to_goal
phases:
- id: approach_1
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  parameters:
    speed:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: contact_1
  type: contact
  generator: linear_cartesian
  control: force_threshold_switch
  termination: contact_detected
  parameters:
    speed:
      type: scalar
      range:
      - 0.005
      - 0.05
- id: push_1
  type: push
  generator: linear_cartesian
  control: impedance_control
  termination: pose_tolerance
  parameters:
    push_depth:
      type: scalar
      range:
      - 0.01
      - 0.1
- id: retract_1
  type: retract
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance

```

## Design Metrics

- **Composite score**: 0.479
- **task_score** (E): 0.722
- **fitness_score**: 0.689  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 0.000
- **Complexity Penalty**: 0.210

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_1 | 1.00 | 1.00 | 0.2835 |
| contact_1 | 1.00 | 1.00 | 0.0445 |
| push_1 | 1.00 | 1.00 | 0.1312 |
| retract_1 | 0.00 | 1.00 | 0.1669 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_1 | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.509, 0.078, 0.033) | (0.513, 0.002, 0.025)→(0.513, 0.002, 0.025) | 0.160→0.160 | 1.00 / 4.000 | 0.245 | 0.245 |
| contact_1 | contact | 1.00 / step_budget | (0.509, 0.078, 0.033)→(0.509, 0.035, 0.021) | (0.513, 0.002, 0.025)→(0.515, -0.004, 0.025) | 0.160→0.154 | 1.00 / 3.333 | 3.092 | 5.584 |
| push_1 | push | 1.00 / step_budget | (0.509, 0.035, 0.021)→(0.504, -0.090, 0.026) | (0.515, -0.004, 0.025)→(0.523, -0.121, 0.029) | 0.154→0.046 | 1.00 / 4.000 | 82.058 | 99.974 |
| retract_1 | retract | 0.00 / step_budget | (0.504, -0.090, 0.026)→(0.497, 0.059, 0.099) | (0.523, -0.121, 0.029)→(0.518, -0.116, 0.025) | 0.046→0.047 | 1.00 / 4.000 | 0.245 | 58.802 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- object_displacement_ratio: 1.000
- lateral_force_integral: None
- approach_alignment: 0.435
- goal_progress: 0.901
- terminal_score: 0.901
- phase_score: 0.794
- phase_breakdown.contact_score: 0.683
- phase_breakdown.approach_score: 0.822
- phase_breakdown.push_score: 0.848

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.836
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 0.901
- **Median Q (composite search score)**: 0.442
- **K-run variance**: 0.0117
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 10.0
- **Parameters at upper bound**: push_1.push_depth
- **Final σ (mean)**: 0.256


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `01fea9f27a58d64b0f9b0ff0cae1096a52b0da1ad311c77058a75ddb9aab77d2`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.0,0.0],"object_xy_delta":[0.06,0.06]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `c53c9bf1992485fcf877d50f4ee23d3483b4b9e63e5a19adda2461c26d89c46e`; realized-scene SHA-256: `35b7946dd60174c5d3e72b05c58367a0800836a817579e6ae5b810157d0560be`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45028,-0.03158,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[0.04972,-0.11842,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.45028,-0.03158,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.08491,"average_solve_count":212.0,"average_success_count":212.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.05681,"contact_1.speed":0.01839,"push_1.push_depth":0.1},"optimized_scores":{"best_composite_score":0.62635,"best_fitness_score":0.83635,"best_task_score":0.90055},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"attachment","body_b":"push_box","contact_count":723.0,"contact_point_centroid":[0.47155,-0.0721,0.02455],"force_p95":17.08419,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":32.94626,"mean_force":4.7259,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46941,-0.06015,0.02036]},{"body_a":"world","body_b":"push_box","contact_count":1610.0,"contact_point_centroid":[0.4689,-0.0952,-5e-05],"force_p95":7.48113,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":26.81791,"mean_force":2.39908,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.46713,-0.05357,0.02061]},{"body_a":"push_box","body_b":"link7","contact_count":14.0,"contact_point_centroid":[0.47759,-0.01594,0.05038],"force_p95":8.71882,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.86603,"mean_force":2.88489,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.44872,-0.00393,0.02107]},{"body_a":"attachment","body_b":"push_box","contact_count":2.0,"contact_point_centroid":[0.49352,-0.13637,0.02001],"force_p95":1.17798,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":1.21244,"mean_force":0.8679,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49351,-0.12439,0.01998]},{"body_a":"world","body_b":"push_box","contact_count":3986.0,"contact_point_centroid":[0.4953,-0.16194,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.84831,"mean_force":0.24633,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.49155,-0.0466,0.05212]},{"body_a":"world","body_b":"push_box","contact_count":3696.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.4737,0.02263,0.16658]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.45028,-0.03158,-1e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24525,"mean_force":0.24525,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.4455,0.02708,0.02713]}],"total_contact_groups":7},"final_pose_error":0.13746,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.49533,-0.16189,0.02499],"final_tcp_position":[0.4934,0.0278,0.08738],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.45028,-0.03158,0.025]},"peak_contact_force":32.94626,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":924.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.025],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3696.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.44886,0.04566,0.03428],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07782,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.45028,-0.03158,0.02499],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.12843,"object_to_goal_dist_start":0.12843,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24525,"tcp_end":[0.44572,0.01191,0.02425],"tcp_start":[0.44886,0.04566,0.03428],"tcp_to_object_dist_end":0.04374,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":868.0,"n_steps_budget":960.0,"object_pos_end":[0.49537,-0.16129,0.02495],"object_pos_start":[0.45028,-0.03158,0.02499],"object_to_goal_dist_end":0.0122,"object_to_goal_dist_start":0.12843,"object_z_max":0.02546,"peak_contact_force":16.0,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":2347.0,"raw_peak_contact_force":32.94626,"tcp_end":[0.49351,-0.12435,0.01999],"tcp_start":[0.44572,0.01191,0.02425],"tcp_to_object_dist_end":0.03732,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.49533,-0.16189,0.02499],"object_pos_start":[0.49537,-0.16129,0.02495],"object_to_goal_dist_end":0.01277,"object_to_goal_dist_start":0.0122,"object_z_max":0.02499,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3988.0,"raw_peak_contact_force":1.21244,"tcp_end":[0.4934,0.0278,0.08738],"tcp_start":[0.49351,-0.12435,0.01999],"tcp_to_object_dist_end":0.1997,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 2 of 3

Configuration SHA-256: `234a0edc218dcf63b67654ddcfd8b0f12da84040687f62c4c4845001a50f549a`; realized-scene SHA-256: `721a00290a47301d7751e432f1a041db545f1b55cfdb74b1d642c32f5b25f702`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.55317,0.00136,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.05317,-0.15136,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.55317,0.00136,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.52308,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.06425,"contact_1.speed":0.0318,"push_1.push_depth":0.1},"optimized_scores":{"best_composite_score":0.44241,"best_fitness_score":0.65241,"best_task_score":0.63722},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":828.0,"contact_point_centroid":[0.56243,-0.04637,0.05406],"force_p95":124.69951,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":142.66812,"mean_force":81.26659,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52752,-0.0313,0.02387]},{"body_a":"world","body_b":"push_box","contact_count":1603.0,"contact_point_centroid":[0.55712,-0.08028,-0.00036],"force_p95":91.90098,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":106.12544,"mean_force":53.4329,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52709,-0.03282,0.02407]},{"body_a":"attachment","body_b":"push_box","contact_count":833.0,"contact_point_centroid":[0.54663,-0.03936,0.05375],"force_p95":84.4124,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":87.51268,"mean_force":51.13371,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.52765,-0.03093,0.02385]},{"body_a":"world","body_b":"push_box","contact_count":3680.0,"contact_point_centroid":[0.53622,-0.10431,-3e-05],"force_p95":0.28497,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":83.22012,"mean_force":0.52908,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50276,-0.0081,0.06647]},{"body_a":"push_box","body_b":"link7","contact_count":51.0,"contact_point_centroid":[0.5507,-0.0956,0.05713],"force_p95":67.90238,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":76.31623,"mean_force":29.23514,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50888,-0.08733,0.03092]},{"body_a":"attachment","body_b":"push_box","contact_count":66.0,"contact_point_centroid":[0.53329,-0.08922,0.06196],"force_p95":46.17858,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":69.45671,"mean_force":16.75423,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50829,-0.08482,0.03148]},{"body_a":"attachment","body_b":"push_box","contact_count":200.0,"contact_point_centroid":[0.55497,0.02172,0.04103],"force_p95":6.90495,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":8.63429,"mean_force":3.06188,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54767,0.03367,0.02052]},{"body_a":"world","body_b":"push_box","contact_count":3142.0,"contact_point_centroid":[0.55339,-0.00155,-1e-05],"force_p95":2.39659,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":6.17705,"mean_force":0.45023,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.54503,0.05401,0.0242]},{"body_a":"world","body_b":"push_box","contact_count":4000.0,"contact_point_centroid":[0.55317,0.00136,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.52208,0.03813,0.16552]}],"total_contact_groups":9},"final_pose_error":0.10222,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.5357,-0.10404,0.02499],"final_tcp_position":[0.50009,0.06046,0.10069],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.55317,0.00136,0.025]},"peak_contact_force":142.66812,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.55317,0.00136,0.02499],"object_pos_start":[0.55317,0.00136,0.025],"object_to_goal_dist_end":0.16043,"object_to_goal_dist_start":0.16043,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":4000.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.54622,0.07657,0.03335],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07599,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":904.0,"n_steps_budget":1000.0,"object_pos_end":[0.55629,-0.00803,0.02516],"object_pos_start":[0.55317,0.00136,0.02499],"object_to_goal_dist_end":0.15273,"object_to_goal_dist_start":0.16043,"object_z_max":0.02524,"peak_contact_force":4.7721,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3342.0,"raw_peak_contact_force":8.63429,"tcp_end":[0.54837,0.02871,0.0197],"tcp_start":[0.54622,0.07657,0.03335],"tcp_to_object_dist_end":0.03797,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":837.0,"n_steps_budget":930.0,"object_pos_end":[0.54125,-0.11578,0.03117],"object_pos_start":[0.55629,-0.00803,0.02516],"object_to_goal_dist_end":0.05395,"object_to_goal_dist_start":0.15273,"object_z_max":0.03119,"peak_contact_force":121.52229,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3264.0,"raw_peak_contact_force":142.66812,"tcp_end":[0.51003,-0.09149,0.02985],"tcp_start":[0.54837,0.02871,0.0197],"tcp_to_object_dist_end":0.03957,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.5357,-0.10404,0.02499],"object_pos_start":[0.54125,-0.11578,0.03117],"object_to_goal_dist_end":0.0582,"object_to_goal_dist_start":0.05395,"object_z_max":0.03456,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3797.0,"raw_peak_contact_force":83.22012,"tcp_end":[0.50009,0.06046,0.10069],"tcp_start":[0.51003,-0.09149,0.02985],"tcp_to_object_dist_end":0.18455,"terminated_normally":false,"termination_reason":"step_budget"}],"success":false}]}
```

### Configuration 3 of 3

Configuration SHA-256: `107d1233d3b0a09f0fa34aa18231b315c9a1d92237bb254399d486ed8004836a`; realized-scene SHA-256: `b2a76c5d1121259d09d3db2c62740fd8fe93dd873d8f379ba1928ff319a7d266`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.5366,0.03695,0.025]},{"name":"goal","value":[0.5,-0.15,0.025]}],"axes":[{"name":"push_direction","value":[-0.0366,-0.18695,0.0]}],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":25.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"push_box","orientation":[1.0,0.0,0.0,0.0],"position":[0.5366,0.03695,0.025]}],"obstacles":[],"targets":[{"name":"task_goal","orientation":[1.0,0.0,0.0,0.0],"position":[0.5,-0.15,0.025]}],"task_name":"push_to_goal"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.73457,"average_solve_count":162.0,"average_success_count":162.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_1.speed":0.09621,"contact_1.speed":0.03354,"push_1.push_depth":0.09958},"optimized_scores":{"best_composite_score":0.3693,"best_fitness_score":0.5793,"best_task_score":0.62809},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"push_box","body_b":"link7","contact_count":805.0,"contact_point_centroid":[0.54862,-0.01142,0.05472],"force_p95":110.59749,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":124.30885,"mean_force":72.50094,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.518,0.0044,0.02322]},{"body_a":"attachment","body_b":"push_box","contact_count":800.0,"contact_point_centroid":[0.53644,-0.00502,0.05213],"force_p95":99.72885,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":106.98451,"mean_force":54.22019,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.51792,0.00405,0.02325]},{"body_a":"push_box","body_b":"link7","contact_count":45.0,"contact_point_centroid":[0.54756,-0.0641,0.05576],"force_p95":85.18964,"geom_a":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":91.97196,"mean_force":40.7413,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50621,-0.05229,0.02975]},{"body_a":"world","body_b":"push_box","contact_count":1551.0,"contact_point_centroid":[0.54268,-0.04659,-0.0003],"force_p95":73.99053,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":91.37117,"mean_force":49.03087,"phase_index":2.0,"phase_name":"push_1","phase_type":"push","tcp_position_centroid":[0.5178,0.00306,0.0234]},{"body_a":"world","body_b":"push_box","contact_count":3697.0,"contact_point_centroid":[0.52388,-0.0832,-3e-05],"force_p95":0.24525,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":87.60218,"mean_force":0.48787,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50061,0.0235,0.07052]},{"body_a":"attachment","body_b":"push_box","contact_count":64.0,"contact_point_centroid":[0.52809,-0.05587,0.05979],"force_p95":64.60894,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":84.52734,"mean_force":23.31559,"phase_index":3.0,"phase_name":"retract_1","phase_type":"retract","tcp_position_centroid":[0.50548,-0.04929,0.03067]},{"body_a":"attachment","body_b":"push_box","contact_count":182.0,"contact_point_centroid":[0.53815,0.05718,0.03786],"force_p95":6.96817,"geom_a":"pusher_tip","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":7.87206,"mean_force":2.71175,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.5313,0.06912,0.02039]},{"body_a":"world","body_b":"push_box","contact_count":2843.0,"contact_point_centroid":[0.53693,0.03432,-1e-05],"force_p95":1.9676,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":5.83239,"mean_force":0.4273,"phase_index":1.0,"phase_name":"contact_1","phase_type":"contact","tcp_position_centroid":[0.52923,0.08899,0.023]},{"body_a":"world","body_b":"push_box","contact_count":3980.0,"contact_point_centroid":[0.5366,0.03695,-1e-05],"force_p95":0.24526,"geom_a":"table","geom_b":"push_box_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.24534,"mean_force":0.24525,"phase_index":0.0,"phase_name":"approach_1","phase_type":"approach","tcp_position_centroid":[0.51452,0.05554,0.16393]}],"total_contact_groups":9},"final_pose_error":0.07286,"key_states":{"actual_goal_position":[0.5,-0.15,0.025],"final_object_position":[0.52325,-0.08307,0.02499],"final_tcp_position":[0.49856,0.08942,0.10954],"realised_goal_position":[0.5,-0.15,0.025],"realised_object_initial_position":[0.5366,0.03695,0.025]},"peak_contact_force":124.30885,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":995.0,"n_steps_budget":1000.0,"object_pos_end":[0.5366,0.03695,0.02499],"object_pos_start":[0.5366,0.03695,0.025],"object_to_goal_dist_end":0.1905,"object_to_goal_dist_start":0.1905,"object_z_max":0.025,"peak_contact_force":0.24525,"phase_name":"approach_1","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":3980.0,"raw_peak_contact_force":0.24534,"tcp_end":[0.53088,0.11128,0.03074],"tcp_start":[0.49978,-0.0,0.30067],"tcp_to_object_dist_end":0.07476,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":3.0,"n_steps":818.0,"n_steps_budget":930.0,"object_pos_end":[0.53943,0.02735,0.02513],"object_pos_start":[0.5366,0.03695,0.02499],"object_to_goal_dist_end":0.18168,"object_to_goal_dist_start":0.1905,"object_z_max":0.0252,"peak_contact_force":4.25895,"phase_name":"contact_1","phase_peak_obstacle_force":0.0,"phase_type":"contact","raw_contact_event_count":3025.0,"raw_peak_contact_force":7.87206,"tcp_end":[0.5319,0.0642,0.01983],"tcp_start":[0.53088,0.11128,0.03074],"tcp_to_object_dist_end":0.03798,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":809.0,"n_steps_budget":900.0,"object_pos_end":[0.53118,-0.08598,0.03116],"object_pos_start":[0.53943,0.02735,0.02513],"object_to_goal_dist_end":0.07148,"object_to_goal_dist_start":0.18168,"object_z_max":0.0312,"peak_contact_force":108.65271,"phase_name":"push_1","phase_peak_obstacle_force":0.0,"phase_type":"push","raw_contact_event_count":3156.0,"raw_peak_contact_force":124.30885,"tcp_end":[0.5071,-0.05559,0.02849],"tcp_start":[0.5319,0.0642,0.01983],"tcp_to_object_dist_end":0.03886,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.52325,-0.08307,0.02499],"object_pos_start":[0.53118,-0.08598,0.03116],"object_to_goal_dist_end":0.07085,"object_to_goal_dist_start":0.07148,"object_z_max":0.03427,"peak_contact_force":0.24525,"phase_name":"retract_1","phase_peak_obstacle_force":0.0,"phase_type":"retract","raw_contact_event_count":3806.0,"raw_peak_contact_force":91.97196,"tcp_end":[0.49856,0.08942,0.10954],"tcp_start":[0.5071,-0.05559,0.02849],"tcp_to_object_dist_end":0.19368,"terminated_normally":false,"termination_reason":"step_budget"}],"success":true}]}
```