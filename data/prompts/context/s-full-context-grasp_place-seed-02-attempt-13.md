## Search State

- **Seed**: 2
- **Iteration**: 14 / 15

### Mutation History (most recent first)

| Iter | Phase Sequence | Generators | Controls | Terminations | Params | Q | task_score | Result |
|---|---|---|---|---|---|---|---|---|
| 13 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | impedance_control | impedance_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.1481 | 0.58 | ❌ rejected |
| 12 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.2399 | 0.76 | ❌ rejected |
| 11 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | linear_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 10 | 0.3599 | 1.00 | ✅ accepted |
| 10 | approach → descend → grasp → lift → approach → descend → release → retract | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | — | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | time_limit | pose_tolerance | 14 | -0.2200 | 0.36 | ❌ rejected |
| 9 | approach → descend → grasp → lift → approach → descend | linear_cartesian | linear_cartesian | — | linear_cartesian | arc_cartesian | linear_cartesian | position_control | position_control | position_control | position_control | position_control | position_control | pose_tolerance | pose_tolerance | grasp_success | pose_tolerance | pose_tolerance | pose_tolerance | 12 | 0.0009 | 0.48 | ❌ rejected |

**Proposal policy**: task_score is 0.58 — NOT near-perfect (target ≥ 0.9). Do NOT hold or make cosmetic tweaks. Make any coherent updates needed to address the diagnosed failure while preserving useful working structure. Use the Mutation History above to avoid repeating failed edits. - task_score ≈ 0: add or repair missing prerequisites, targets, guard/retry logic, generator/control choices, subtasks, or phase-ordering errors that block task progress.
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

- Task name: grasp_place
- Frozen realised-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`
- Frozen object start: [0.4761612134249316, -0.02015088565858767, 0.03]
- Frozen task target: [0.631422574059428, 0.1591915942135097, 0.1900150788948481]
- Goal object position: (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- place_goal_position (task success criterion — final object 3D position must be close to the realised airborne target here): (0.631422574059428, 0.1591915942135097, 0.1900150788948481)
- Grasp/lift components are optimiser fitness diagnostics only; canonical task_score is final object-to-realised-target proximity.
- Object initial pose: (0.4761612134249316, -0.02015088565858767, 0.03)
- Goal tolerance: 0.02 m
- Expressivity sigma: 0.15 m
- Expressivity threshold: 0.3
- Force limit: 20.0 N
- Robot initial TCP position: (0.5, 0.0, 0.3)
- Robot initial gripper state: **open** (gripper starts fully open; ensure a `grasp`/`force_grasp` phase closes it before lifting)
- Phase navigation guidance: the task `phase_target_map` may provide internal predefined TCP waypoint aliases / semantic phase ids. These names are not DSL phase types and are intentionally not enumerated here to avoid confusing ids with types. Phase `id` may be semantic, but phase `type` must be exactly one of the DSL enum values listed in the prompt.
- Primary evaluation target: **final object-to-realised-airborne-3D-target proximity. Grasp/lift signals are optimiser fitness diagnostics only; they do not gate the canonical task_score.**

## Scene Entities

robot:
  model: panda_full
  tcp_site: attachment_site
  gripper: franka_hand
  tcp_initial_world: [0.5, 0, 0.3]
objects:
  - name: grasp_target
    role: manipulated_object
    dynamics: free
    geometry: box
    dimensions_m: [0.04, 0.04, 0.06]
    mass_kg: 0.05
  - name: placement_surface
    role: goal_area
    dynamics: static
    geometry: point
task_landmarks:
  frozen_object_start: [0.4762, -0.0202, 0.03]
  frozen_task_target: [0.6314, 0.1592, 0.19]
  frozen_object_starts: {'grasp_target': [0.4761612134249316, -0.02015088565858767, 0.03]}
  frozen_targets: {'place_target': [0.631422574059428, 0.1591915942135097, 0.1900150788948481]}
  goal_tolerance_m: 0.02
  force_limit_n: 20
  force_scale_n: 5
  realized_scene_sha256: 67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a

> ⚠️ **SUBTASK STRUCTURE CAUTION**: The current best task_score is 1.000, which indicates the subtask decomposition is already effective.
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
| `object` | offset from object initial position (0.4761612134249316, -0.02015088565858767, 0.03) | approach/contact targets near object start |
| `goal` | offset from task goal position (0.631422574059428, 0.1591915942135097, 0.1900150788948481) | final destination targets |
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

## Current Skill (Q=0.148) — your mutation base

```yaml
skill: grasp_place
dsl_version: 2
subtasks:
- id: approach_object
  anchor: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: grasp_object
  anchor: object
  target_entity: object
  weight: 0.2
- id: lift_object
  anchor: object
  target_entity: object
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: approach_goal
  offset:
  - 0.0
  - 0.0
  - 0.15
  weight: 0.2
- id: place_object
  target_entity: object
  weight: 0.2
phases:
- id: approach_above_object
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_height:
      type: scalar
      range:
      - 0.1
      - 0.25
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_speed:
      type: scalar
      range:
      - 0.05
      - 0.3
      default: 0.15
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_object
- id: descend_to_grasp
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_object
    entity: grasp_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    descent_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    grasp_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: grasp_object
- id: grasp
  type: grasp
  control: position_control
  termination: grasp_success
  end_effector_action: force_grasp
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
  guards:
  - id: grasp_guard
    when: after_phase
    predicate: bilateral_grasp
    threshold: 0.5
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - -0.005
  subtask_id: grasp_object
- id: lift
  type: lift
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: current_tcp
    offset:
    - 0.0
    - 0.0
    - 0.0
    offset_along_axis:
      distance: 0.15
      axis: world_z
      mode: add_to_offset
      sign: positive
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    lift_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset_along_axis.distance
        mode: replace
    lift_speed:
      type: scalar
      range:
      - 0.03
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  guards:
  - id: lift_guard
    when: after_phase
    predicate: object_lifted
    threshold: 0.03
    on_failure: retry
  retries:
    max_attempts: 1
    strategy: offset_target
    offset:
    - 0.0
    - 0.0
    - 0.005
  subtask_id: lift_object
- id: approach_above_goal
  type: approach
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.15
    tolerance: 0.02
    orientation:
      mode: keep_current
  parameters:
    approach_goal_height:
      type: scalar
      range:
      - 0.1
      - 0.2
      default: 0.15
      binds_to:
      - path: target.offset.z
        mode: replace
    approach_goal_speed:
      type: scalar
      range:
      - 0.02
      - 0.15
      default: 0.08
      binds_to:
      - path: generator.speed
        mode: replace
  subtask_id: approach_goal
- id: descend_to_place
  type: descend
  generator: linear_cartesian
  control: position_control
  termination: pose_tolerance
  target:
    source: yaml
    anchor: task_goal
    entity: place_target
    offset:
    - 0.0
    - 0.0
    - 0.0
    tolerance: 0.01
    orientation:
      mode: keep_current
  parameters:
    place_speed:
      type: scalar
      range:
      - 0.02
      - 0.1
      default: 0.05
      binds_to:
      - path: generator.speed
        mode: replace
    place_z_tolerance:
      type: scalar
      range:
      - 0.005
      - 0.02
      default: 0.01
      binds_to:
      - path: termination.pose_tolerance
        mode: replace
  subtask_id: place_object

```

## Executable Phase Semantics

Visible executable target/binding metadata from the compiled controller:
- **approach_above_object** (`approach`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_height: status=consumed; consumers=target.offset.z (replace)
    - approach_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_grasp** (`descend`)
  - target: source=yaml, anchor=task_object, entity=grasp_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - descent_speed: status=consumed; consumers=generator.speed (replace)
    - grasp_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)
- **grasp** (`grasp`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0]
  - parameter_bindings: none
  - guards:
    - id=grasp_guard, when=after_phase, predicate=bilateral_grasp, on_failure=retry, threshold=0.5
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, -0.005]
- **lift** (`lift`)
  - target: source=yaml, anchor=current_tcp, offset=[0.0, 0.0, 0.0], offset_along_axis={axis=world_z, distance=0.15, mode=add_to_offset, sign=positive}, tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - lift_height: status=consumed; consumers=target.offset_along_axis.distance (replace)
    - lift_speed: status=consumed; consumers=generator.speed (replace)
  - guards:
    - id=lift_guard, when=after_phase, predicate=object_lifted, on_failure=retry, threshold=0.03
  - retries: max_attempts=1, strategy=offset_target, offset=[0.0, 0.0, 0.005]
- **approach_above_goal** (`approach`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.15], tolerance=0.02
  - orientation: mode=keep_current
  - parameter_bindings:
    - approach_goal_height: status=consumed; consumers=target.offset.z (replace)
    - approach_goal_speed: status=consumed; consumers=generator.speed (replace)
- **descend_to_place** (`descend`)
  - target: source=yaml, anchor=task_goal, entity=place_target, offset=[0.0, 0.0, 0.0], tolerance=0.01
  - orientation: mode=keep_current
  - parameter_bindings:
    - place_speed: status=consumed; consumers=generator.speed (replace)
    - place_z_tolerance: status=consumed; consumers=termination.pose_tolerance (replace)

## Design Metrics

- **Composite score**: 0.148
- **task_score** (E): 0.576
- **fitness_score**: 0.768  *(CMA-ES inner optimisation target; = task_score for most tasks; includes phase progress bonus for contact-rich tasks)*
- **Termination Fidelity** (C): 0.000
  → phases frequently time out instead of reaching designed conditions
- **Force Compliance**: 1.000
- **Complexity Penalty**: 0.620

## Per-Phase Performance

| Phase | Normal Term. Rate | Contact Rate | Mean Displacement (m) |
|-------|-------------------|--------------|------------------------|
| approach_above_object | 1.00 | 1.00 | 0.0549 |
| descend_to_grasp | 1.00 | 1.00 | 0.2197 |
| grasp | 1.00 | 1.00 | 0.0117 |
| lift | 0.67 | 1.00 | 0.0981 |
| approach_above_goal | 1.00 | 1.00 | 0.2786 |
| descend_to_place | 1.00 | 1.00 | 0.0968 |

## Last Optimised Execution State

Mean phase-boundary state across the latest CMA-ES optimised traces (up to 8 phases; values rounded to 3 decimals).

| Phase | Type | Normal / reason | TCP start→end | Object start→end | Obj→goal start→end | Contact rate / events | Peak force | Raw peak force |
|---|---|---|---|---|---|---|---|---|
| approach_above_object | approach | 1.00 / step_budget | (0.500, -0.000, 0.301)→(0.496, -0.009, 0.254) | (0.493, -0.015, 0.030)→(0.493, -0.015, 0.026) | 0.279→0.281 | 1.00 / 4.000 | 9.683 | 0.138 |
| descend_to_grasp | descend | 1.00 / step_budget | (0.496, -0.009, 0.254)→(0.489, -0.015, 0.035) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 4.000 | 0.123 | 0.124 |
| grasp | grasp | 1.00 / step_budget | (0.489, -0.015, 0.035)→(0.481, -0.015, 0.026) | (0.493, -0.015, 0.026)→(0.493, -0.015, 0.026) | 0.281→0.281 | 1.00 / 45.000 | 0.138 | 0.202 |
| lift | lift | 0.67 / step_budget | (0.481, -0.015, 0.026)→(0.477, -0.015, 0.124) | (0.493, -0.015, 0.026)→(0.489, -0.015, 0.115) | 0.281→0.250 | 1.00 / 34.000 | 524.414 | 0.690 |
| approach_above_goal | approach | 1.00 / step_budget | (0.477, -0.015, 0.124)→(0.623, 0.162, 0.268) | (0.489, -0.015, 0.115)→(0.603, 0.123, 0.102) | 0.250→0.135 | 1.00 / 19.333 | 3249.695 | 1.193 |
| descend_to_place | descend | 1.00 / step_budget | (0.623, 0.162, 0.268)→(0.631, 0.172, 0.172) | (0.603, 0.123, 0.102)→(0.609, 0.129, 0.070) | 0.135→0.109 | 1.00 / 18.000 | 0.106 | 0.131 |

## Task Sub-Scores

These are diagnostics / optimiser fitness-shaping signals, not a guaranteed decomposition of canonical task_score.

- grasp_success_rate: 1.000
- place_accuracy: 0.429
- lift_clearance: 1.000
- transport_retention: None
- terminal_score: 1.000
- phase_score: 0.466
- phase_breakdown.approach_object_score: 0.123
- phase_breakdown.grasp_object_score: 0.787
- phase_breakdown.lift_object_score: 0.293
- phase_breakdown.approach_goal_score: 0.305
- phase_breakdown.place_object_score: 0.821
- grasp_place_fitness: 0.981

## CMA-ES Diagnostics

- **Best shaped reward** (fitness_score): 0.981
  *(shaped task+phase signal; this is the CMA-ES objective)*
- **Best task_score**: 1.000
- **Median Q (composite search score)**: 0.096
- **K-run variance**: 0.0248
- **Stagnated**: no
- **Stop reason**: budget_exhausted
- **Mean generations**: 7.0
- **Final σ (mean)**: 0.286


## Frozen randomized evaluation bank (shared across every structure)

Bank SHA-256: `dde525b5f1d1bd9dc458c18c8bb170b8849a392c0909c5e3e8e19baca2e18946`. Stable order: configuration 1 to configuration 3.

### Nominal task randomization distribution and ranges

These nominal ranges define how the fixed bank was sampled and remain valid alongside the realized facts below.

```json
{"distribution":"independent_uniform","parameters":{"enabled":true,"goal_xy_delta":[0.05,0.05],"goal_z_delta":0.15,"object_xy_delta":[0.05,0.05]},"range_semantics":{"*_xy_delta":"independent per-axis draws in [-delta, +delta]","goal_z_delta":"draw in [0, max_delta]","hinge_delta_deg":"draw in [-delta_deg, +delta_deg]"}}
```

### Configuration 1 of 3

Configuration SHA-256: `3eaf951d4314ad541ffae42f4c615c856bb77d128e3ae1cab520a1988305ba67`; realized-scene SHA-256: `67b45068113fe0ef6f199d4981822d51bd0bd66bb4f388f7402a08094b41852a`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.47616,-0.02015,0.03]},{"name":"goal","value":[0.63142,0.15919,0.19002]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.47616,-0.02015,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63142,0.15919,0.19002]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.15101,"average_solve_count":298.0,"average_success_count":298.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.1307,"approach_above_goal.approach_goal_speed":0.05009,"approach_above_object.approach_height":0.24145,"approach_above_object.approach_speed":0.15228,"descend_to_grasp.descent_speed":0.0938,"descend_to_grasp.grasp_z_tolerance":0.01383,"descend_to_place.place_speed":0.0515,"descend_to_place.place_z_tolerance":0.0095,"lift.lift_height":0.18313,"lift.lift_speed":0.03051},"optimized_scores":{"best_composite_score":0.36147,"best_fitness_score":0.98147,"best_task_score":1.0},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":175.0,"contact_point_centroid":[0.47118,-0.01884,-0.00122],"force_p95":0.50114,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.57391,"mean_force":0.12876,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46298,-0.01928,0.02863]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19492.0,"contact_point_centroid":[0.46044,-1e-05,0.0745],"force_p95":0.07492,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24074,"mean_force":0.05145,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46049,-0.01921,0.07225]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21116.0,"contact_point_centroid":[0.46031,-0.03831,0.07637],"force_p95":0.07097,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.2405,"mean_force":0.0482,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.46048,-0.01921,0.07441]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.47617,-0.01997,-0.00208],"force_p95":0.14521,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22272,"mean_force":0.12883,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.46572,-0.01934,0.02825]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5670.0,"contact_point_centroid":[0.61664,0.1648,0.24255],"force_p95":0.07426,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14775,"mean_force":0.0526,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61585,0.1458,0.24238]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5302.0,"contact_point_centroid":[0.61672,0.12711,0.24094],"force_p95":0.08518,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.14048,"mean_force":0.05564,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.61621,0.14619,0.24028]},{"body_a":"world","body_b":"grasp_target","contact_count":204.0,"contact_point_centroid":[0.47616,-0.02015,-0.00136],"force_p95":0.13839,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12472,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.49437,-0.00385,0.29321]},{"body_a":"world","body_b":"grasp_target","contact_count":3084.0,"contact_point_centroid":[0.47616,-0.02015,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12666,"mean_force":0.12265,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.47884,-0.01441,0.15762]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4814.0,"contact_point_centroid":[0.46455,-7e-05,0.02938],"force_p95":0.0684,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10233,"mean_force":0.0449,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4646,-0.01931,0.02715]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":21188.0,"contact_point_centroid":[0.53571,0.0427,0.20739],"force_p95":0.06812,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09915,"mean_force":0.04662,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53553,0.0618,0.20575]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":19500.0,"contact_point_centroid":[0.53777,0.08297,0.2098],"force_p95":0.07362,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09049,"mean_force":0.0501,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.53744,0.06378,0.20791]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5436.0,"contact_point_centroid":[0.46404,-0.03856,0.02879],"force_p95":0.06541,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08177,"mean_force":0.04112,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4646,-0.01932,0.02716]}],"total_contact_groups":12},"final_pose_error":0.00985,"key_states":{"actual_goal_position":[0.63142,0.15919,0.19002],"final_object_position":[0.63073,0.15499,0.17942],"final_tcp_position":[0.62469,0.15503,0.19587],"realised_goal_position":[0.63142,0.15919,0.19002],"realised_object_initial_position":[0.47616,-0.02015,0.03]},"peak_contact_force":0.57391,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":52.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02587],"object_pos_start":[0.47616,-0.02015,0.03],"object_to_goal_dist_end":0.28847,"object_to_goal_dist_start":0.28614,"object_z_max":0.03,"peak_contact_force":0.12703,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":204.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.48736,-0.00935,0.2837],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.2583,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":771.0,"n_steps_budget":1000.0,"object_pos_end":[0.47616,-0.02015,0.02602],"object_pos_start":[0.47616,-0.02015,0.02587],"object_to_goal_dist_end":0.28838,"object_to_goal_dist_start":0.28847,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":3084.0,"raw_peak_contact_force":0.12666,"subtask_id":"grasp_object","tcp_end":[0.47245,-0.01947,0.03493],"tcp_start":[0.48736,-0.00935,0.2837],"tcp_to_object_dist_end":0.00968,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":46.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.47604,-0.01934,0.02573],"object_pos_start":[0.47616,-0.02015,0.02602],"object_to_goal_dist_end":0.28811,"object_to_goal_dist_start":0.28838,"object_z_max":0.02602,"peak_contact_force":0.14151,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12050.0,"raw_peak_contact_force":0.22272,"subtask_id":"grasp_object","tcp_end":[0.46457,-0.01931,0.02712],"tcp_start":[0.47245,-0.01947,0.03493],"tcp_to_object_dist_end":0.01155,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.46909,-0.0191,0.11211],"object_pos_start":[0.47604,-0.01934,0.02573],"object_to_goal_dist_end":0.25339,"object_to_goal_dist_start":0.28811,"object_z_max":0.11202,"peak_contact_force":0.0711,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":40783.0,"raw_peak_contact_force":0.57391,"subtask_id":"lift_object","tcp_end":[0.46054,-0.0192,0.12066],"tcp_start":[0.46457,-0.01931,0.02712],"tcp_to_object_dist_end":0.01209,"terminated_normally":false,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":42.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.61516,0.13783,0.27452],"object_pos_start":[0.46909,-0.0191,0.11211],"object_to_goal_dist_end":0.08867,"object_to_goal_dist_start":0.25339,"object_z_max":0.27438,"peak_contact_force":0.06723,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":40688.0,"raw_peak_contact_force":0.09915,"subtask_id":"approach_goal","tcp_end":[0.60936,0.13784,0.28915],"tcp_start":[0.46054,-0.0192,0.12066],"tcp_to_object_dist_end":0.01573,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":295.0,"n_steps_budget":1000.0,"object_pos_end":[0.63073,0.15499,0.17942],"object_pos_start":[0.61516,0.13783,0.27452],"object_to_goal_dist_end":0.01142,"object_to_goal_dist_start":0.08867,"object_z_max":0.27458,"peak_contact_force":0.07151,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":10972.0,"raw_peak_contact_force":0.14775,"subtask_id":"place_object","tcp_end":[0.62469,0.15503,0.19587],"tcp_start":[0.60936,0.13784,0.28915],"tcp_to_object_dist_end":0.01753,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 2 of 3

Configuration SHA-256: `92fc0f2bbc35407e7976a239cbab7bb266e8a517486aa3be6bd6666f4c63f38d`; realized-scene SHA-256: `5ce27bcdb8582e1d517b17df0f9c2ad7b05701113a75707627744a889253e6a7`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.45856,-0.02632,0.03]},{"name":"goal","value":[0.63013,0.20822,0.11412]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.45856,-0.02632,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.63013,0.20822,0.11412]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.75743,"average_solve_count":202.0,"average_success_count":202.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.10004,"approach_above_goal.approach_goal_speed":0.09171,"approach_above_object.approach_height":0.20316,"approach_above_object.approach_speed":0.07499,"descend_to_grasp.descent_speed":0.06922,"descend_to_grasp.grasp_z_tolerance":0.01089,"descend_to_place.place_speed":0.08195,"descend_to_place.place_z_tolerance":0.01555,"lift.lift_height":0.11566,"lift.lift_speed":0.12486},"optimized_scores":{"best_composite_score":0.09612,"best_fitness_score":0.71612,"best_task_score":0.46881},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":679.0,"contact_point_centroid":[0.60356,0.15736,-0.00345],"force_p95":0.67668,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.85105,"mean_force":0.18785,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.60376,0.17846,0.19565]},{"body_a":"world","body_b":"grasp_target","contact_count":133.0,"contact_point_centroid":[0.45575,-0.02511,-0.00126],"force_p95":0.5536,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.77339,"mean_force":0.10864,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44595,-0.02538,0.02955]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":8789.0,"contact_point_centroid":[0.44519,-0.00623,0.07399],"force_p95":0.10347,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3204,"mean_force":0.06232,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44365,-0.02528,0.0718]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":9469.0,"contact_point_centroid":[0.4452,-0.04425,0.073],"force_p95":0.1005,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31833,"mean_force":0.05874,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.44362,-0.02528,0.07135]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":6694.0,"contact_point_centroid":[0.51128,0.07529,0.15409],"force_p95":0.13689,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24746,"mean_force":0.09247,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50642,0.05693,0.15523]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.45858,-0.02615,-0.00208],"force_p95":0.14582,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.22361,"mean_force":0.12902,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.44838,-0.02546,0.02897]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6902.0,"contact_point_centroid":[0.50999,0.03673,0.15353],"force_p95":0.13132,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.19416,"mean_force":0.09069,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.50497,0.05507,0.15465]},{"body_a":"world","body_b":"grasp_target","contact_count":492.0,"contact_point_centroid":[0.45856,-0.02632,-0.00174],"force_p95":0.13797,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.12362,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.48518,-0.00855,0.27559]},{"body_a":"world","body_b":"grasp_target","contact_count":900.0,"contact_point_centroid":[0.60354,0.1574,-0.00199],"force_p95":0.12264,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12268,"mean_force":0.12262,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.62039,0.20059,0.16171]},{"body_a":"world","body_b":"grasp_target","contact_count":2824.0,"contact_point_centroid":[0.45856,-0.02632,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.46063,-0.02208,0.14029]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5283.0,"contact_point_centroid":[0.44669,-0.00618,0.02948],"force_p95":0.06578,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.10469,"mean_force":0.04114,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4473,-0.02543,0.02795]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":5440.0,"contact_point_centroid":[0.44669,-0.04472,0.02934],"force_p95":0.06582,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.08186,"mean_force":0.04118,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.4473,-0.02543,0.02795]},{"body_a":"left_finger","body_b":"right_finger","contact_count":470.0,"contact_point_centroid":[0.60948,0.18521,0.20026],"force_p95":0.01325,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01505,"mean_force":0.0109,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.60921,0.1852,0.19789]},{"body_a":"left_finger","body_b":"right_finger","contact_count":943.0,"contact_point_centroid":[0.6208,0.20062,0.16363],"force_p95":0.01102,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01279,"mean_force":0.01062,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.6204,0.2006,0.16154]}],"total_contact_groups":14},"final_pose_error":0.00995,"key_states":{"actual_goal_position":[0.63013,0.20822,0.11412],"final_object_position":[0.60354,0.1574,0.01602],"final_tcp_position":[0.62393,0.20475,0.12109],"realised_goal_position":[0.63013,0.20822,0.11412],"realised_object_initial_position":[0.45856,-0.02632,0.03]},"peak_contact_force":1573.09317,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":124.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.03],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30252,"object_z_max":0.03,"peak_contact_force":28.79943,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":492.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.46878,-0.01856,0.24848],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.22283,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":706.0,"n_steps_budget":1000.0,"object_pos_end":[0.45856,-0.02632,0.02602],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30365,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2824.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.45489,-0.02568,0.03517],"tcp_start":[0.46878,-0.01856,0.24848],"tcp_to_object_dist_end":0.00988,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":48.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.45845,-0.02551,0.02572],"object_pos_start":[0.45856,-0.02632,0.02602],"object_to_goal_dist_end":0.30318,"object_to_goal_dist_start":0.30365,"object_z_max":0.02602,"peak_contact_force":0.14279,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":12523.0,"raw_peak_contact_force":0.22361,"subtask_id":"grasp_object","tcp_end":[0.44727,-0.02542,0.02792],"tcp_start":[0.45489,-0.02568,0.03517],"tcp_to_object_dist_end":0.01139,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":23.0,"n_steps":534.0,"n_steps_budget":600.0,"object_pos_end":[0.46135,-0.02527,0.11975],"object_pos_start":[0.45845,-0.02551,0.02572],"object_to_goal_dist_end":0.28816,"object_to_goal_dist_start":0.30318,"object_z_max":0.11962,"peak_contact_force":1573.09317,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":18391.0,"raw_peak_contact_force":0.77339,"subtask_id":"lift_object","tcp_end":[0.44361,-0.02526,0.13114],"tcp_start":[0.44727,-0.02542,0.02792],"tcp_to_object_dist_end":0.02108,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":917.0,"n_steps_budget":1000.0,"object_pos_end":[0.60354,0.1574,0.01601],"object_pos_start":[0.46135,-0.02527,0.11975],"object_to_goal_dist_end":0.11364,"object_to_goal_dist_start":0.28816,"object_z_max":0.15847,"peak_contact_force":0.12269,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":14745.0,"raw_peak_contact_force":1.85105,"subtask_id":"approach_goal","tcp_end":[0.61898,0.1973,0.20187],"tcp_start":[0.44361,-0.02526,0.13114],"tcp_to_object_dist_end":0.19072,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":225.0,"n_steps_budget":1000.0,"object_pos_end":[0.60354,0.1574,0.01602],"object_pos_start":[0.60354,0.1574,0.01601],"object_to_goal_dist_end":0.11363,"object_to_goal_dist_start":0.11364,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":1843.0,"raw_peak_contact_force":0.12268,"subtask_id":"place_object","tcp_end":[0.62393,0.20475,0.12109],"tcp_start":[0.61898,0.1973,0.20187],"tcp_to_object_dist_end":0.11704,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```

### Configuration 3 of 3

Configuration SHA-256: `a3b2449a94ded39f3d450008c4da002b4ddf87103ab7d1b86900d116c316ff53`; realized-scene SHA-256: `1959b3932a54fd3d3850620783d44a63a35b8fa059f78d939fdbdef5fbfc64e8`.

<!-- skill-synthesis:realized-scene:v1 -->

Realized scene facts (concise typed schema):

```json
{"anchors":[{"name":"object","value":[0.54431,0.00113,0.03]},{"name":"goal","value":[0.64762,0.15808,0.1911]}],"axes":[],"fixture_states":[],"fixtures":[],"limits":[{"name":"goal_tolerance_m","value":0.02},{"name":"force_limit_n","value":20.0},{"name":"force_scale_n","value":5.0}],"object_starts":[{"name":"grasp_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.54431,0.00113,0.03]}],"obstacles":[],"targets":[{"name":"place_target","orientation":[1.0,0.0,0.0,0.0],"position":[0.64762,0.15808,0.1911]}],"task_name":"grasp_place"}
```

Aligned optimization and replay/contact feedback:

```json
{"averaged_ik_statistics":{"available":true,"average_failure_count":0.0,"average_failure_rate":0.0,"average_mean_iterations":3.64103,"average_solve_count":195.0,"average_success_count":195.0,"replay_count":1},"omitted_parameter_count":0,"optimized_parameters":{"approach_above_goal.approach_goal_height":0.13885,"approach_above_goal.approach_goal_speed":0.11044,"approach_above_object.approach_height":0.18462,"approach_above_object.approach_speed":0.16572,"descend_to_grasp.descent_speed":0.09185,"descend_to_grasp.grasp_z_tolerance":0.00866,"descend_to_place.place_speed":0.06886,"descend_to_place.place_z_tolerance":0.01339,"lift.lift_height":0.134,"lift.lift_speed":0.06028},"optimized_scores":{"best_composite_score":-0.01327,"best_fitness_score":0.60673,"best_task_score":0.25977},"replay_outcomes":[{"contacts":{"omitted_contact_groups":0,"reported_contact_groups":[{"body_a":"world","body_b":"grasp_target","contact_count":1508.0,"contact_point_centroid":[0.5921,0.0737,-0.0027],"force_p95":0.34782,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":1.62904,"mean_force":0.15882,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.61783,0.12219,0.27485]},{"body_a":"world","body_b":"grasp_target","contact_count":201.0,"contact_point_centroid":[0.53928,0.0006,-0.00114],"force_p95":0.48412,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.72153,"mean_force":0.11371,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52775,0.00082,0.0254]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":6268.0,"contact_point_centroid":[0.55332,0.01795,0.16242],"force_p95":0.14461,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.3948,"mean_force":0.07764,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.55006,0.03652,0.16311]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":18585.0,"contact_point_centroid":[0.52625,-0.01831,0.07476],"force_p95":0.0783,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.32013,"mean_force":0.05498,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52521,0.00078,0.07283]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":18996.0,"contact_point_centroid":[0.52625,0.01985,0.07359],"force_p95":0.07769,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.31098,"mean_force":0.05409,"phase_index":3.0,"phase_name":"lift","phase_type":"lift","tcp_position_centroid":[0.52523,0.00078,0.07179]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":5879.0,"contact_point_centroid":[0.5524,0.05432,0.16117],"force_p95":0.15466,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.24071,"mean_force":0.0805,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.54934,0.03559,0.16191]},{"body_a":"world","body_b":"grasp_target","contact_count":1800.0,"contact_point_centroid":[0.54429,0.00098,-0.00203],"force_p95":0.13176,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.16054,"mean_force":0.1253,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.53101,0.00088,0.02527]},{"body_a":"world","body_b":"grasp_target","contact_count":628.0,"contact_point_centroid":[0.54431,0.00113,-0.0018],"force_p95":0.13781,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.13845,"mean_force":0.1234,"phase_index":0.0,"phase_name":"approach_above_object","phase_type":"approach","tcp_position_centroid":[0.51461,0.0004,0.26574]},{"body_a":"world","body_b":"grasp_target","contact_count":2384.0,"contact_point_centroid":[0.54431,0.00113,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12264,"mean_force":0.12263,"phase_index":1.0,"phase_name":"descend_to_grasp","phase_type":"descend","tcp_position_centroid":[0.53361,0.00091,0.13008]},{"body_a":"world","body_b":"grasp_target","contact_count":1184.0,"contact_point_centroid":[0.59179,0.07376,-0.00199],"force_p95":0.12263,"geom_a":"table","geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":false,"involves_task_object":true,"max_force":0.12263,"mean_force":0.12263,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64157,0.15325,0.25696]},{"body_a":"left_finger","body_b":"grasp_target","contact_count":4115.0,"contact_point_centroid":[0.5308,-0.01834,0.02653],"force_p95":0.07605,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.11017,"mean_force":0.0517,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52975,0.00086,0.02384]},{"body_a":"right_finger","body_b":"grasp_target","contact_count":4878.0,"contact_point_centroid":[0.53074,0.01994,0.02565],"force_p95":0.06805,"geom_b":"grasp_target_geom","involves_obstacle":false,"involves_robot_link":true,"involves_task_object":true,"max_force":0.09675,"mean_force":0.04481,"phase_index":2.0,"phase_name":"grasp","phase_type":"grasp","tcp_position_centroid":[0.52976,0.00086,0.02384]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1429.0,"contact_point_centroid":[0.62089,0.12546,0.28145],"force_p95":0.01183,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01624,"mean_force":0.01064,"phase_index":4.0,"phase_name":"approach_above_goal","phase_type":"approach","tcp_position_centroid":[0.62045,0.12545,0.27914]},{"body_a":"left_finger","body_b":"right_finger","contact_count":1269.0,"contact_point_centroid":[0.64209,0.15329,0.25872],"force_p95":0.01098,"involves_obstacle":false,"involves_robot_link":true,"involves_task_object":false,"max_force":0.01256,"mean_force":0.0104,"phase_index":5.0,"phase_name":"descend_to_place","phase_type":"descend","tcp_position_centroid":[0.64159,0.15328,0.25652]}],"total_contact_groups":14},"final_pose_error":0.00972,"key_states":{"actual_goal_position":[0.64762,0.15808,0.1911],"final_object_position":[0.59179,0.07376,0.01602],"final_tcp_position":[0.6434,0.1561,0.19963],"realised_goal_position":[0.64762,0.15808,0.1911],"realised_object_initial_position":[0.54431,0.00113,0.03]},"peak_contact_force":9748.8954,"phases":[{"contact_detected":true,"contact_event_count":4.0,"n_steps":158.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.03],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.24751,"object_z_max":0.03,"peak_contact_force":0.12264,"phase_name":"approach_above_object","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":628.0,"raw_peak_contact_force":0.13845,"subtask_id":"approach_object","tcp_end":[0.53123,0.00082,0.22958],"tcp_start":[0.49977,-0.0,0.30085],"tcp_to_object_dist_end":0.20398,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":4.0,"n_steps":596.0,"n_steps_budget":1000.0,"object_pos_end":[0.54431,0.00113,0.02602],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25012,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12263,"phase_name":"descend_to_grasp","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2384.0,"raw_peak_contact_force":0.12264,"subtask_id":"grasp_object","tcp_end":[0.53846,0.00102,0.0339],"tcp_start":[0.53123,0.00082,0.22958],"tcp_to_object_dist_end":0.00981,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":41.0,"n_steps":50.0,"n_steps_budget":50.0,"object_pos_end":[0.54415,0.00073,0.02588],"object_pos_start":[0.54431,0.00113,0.02602],"object_to_goal_dist_end":0.25053,"object_to_goal_dist_start":0.25012,"object_z_max":0.02602,"peak_contact_force":0.12964,"phase_name":"grasp","phase_peak_obstacle_force":0.0,"phase_type":"grasp","raw_contact_event_count":10793.0,"raw_peak_contact_force":0.16054,"subtask_id":"grasp_object","tcp_end":[0.52972,0.00086,0.0238],"tcp_start":[0.53846,0.00102,0.0339],"tcp_to_object_dist_end":0.01458,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":38.0,"n_steps":1000.0,"n_steps_budget":1000.0,"object_pos_end":[0.53692,0.00079,0.11201],"object_pos_start":[0.54415,0.00073,0.02588],"object_to_goal_dist_end":0.20797,"object_to_goal_dist_start":0.25053,"object_z_max":0.11191,"peak_contact_force":0.07819,"phase_name":"lift","phase_peak_obstacle_force":0.0,"phase_type":"lift","raw_contact_event_count":37782.0,"raw_peak_contact_force":0.72153,"subtask_id":"lift_object","tcp_end":[0.52535,0.00079,0.12109],"tcp_start":[0.52972,0.00086,0.0238],"tcp_to_object_dist_end":0.0147,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":950.0,"n_steps_budget":1000.0,"object_pos_end":[0.59179,0.07376,0.01602],"object_pos_start":[0.53692,0.00079,0.11201],"object_to_goal_dist_end":0.2022,"object_to_goal_dist_start":0.20797,"object_z_max":0.19316,"peak_contact_force":9748.8954,"phase_name":"approach_above_goal","phase_peak_obstacle_force":0.0,"phase_type":"approach","raw_contact_event_count":15084.0,"raw_peak_contact_force":1.62904,"subtask_id":"approach_goal","tcp_end":[0.641,0.151,0.31266],"tcp_start":[0.52535,0.00079,0.12109],"tcp_to_object_dist_end":0.31046,"terminated_normally":true,"termination_reason":"step_budget"},{"contact_detected":true,"contact_event_count":8.0,"n_steps":296.0,"n_steps_budget":1000.0,"object_pos_end":[0.59179,0.07376,0.01602],"object_pos_start":[0.59179,0.07376,0.01602],"object_to_goal_dist_end":0.2022,"object_to_goal_dist_start":0.2022,"object_z_max":0.01602,"peak_contact_force":0.12263,"phase_name":"descend_to_place","phase_peak_obstacle_force":0.0,"phase_type":"descend","raw_contact_event_count":2453.0,"raw_peak_contact_force":0.12263,"subtask_id":"place_object","tcp_end":[0.6434,0.1561,0.19963],"tcp_start":[0.641,0.151,0.31266],"tcp_to_object_dist_end":0.20774,"terminated_normally":true,"termination_reason":"step_budget"}],"success":true}]}
```